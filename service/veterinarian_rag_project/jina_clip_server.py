# file: embed_api.py
# pip install fastapi uvicorn transformers onnxruntime pillow requests pydantic
# 可选：pip install torch（image_processor 默认 return_tensors='pt'，若无 torch 可改成 'np'）
import os
import io
import time
import base64
from typing import Optional

import numpy as np
import requests
from PIL import Image
import onnxruntime as ort
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from transformers import AutoImageProcessor, AutoTokenizer

# =========================
# 环境变量与常量
# =========================
MODEL_DIR  = os.getenv("MODEL_DIR", "/home/wmy/workspace/model_zoo/jinaai/jina-clip-v2")
ONNX_PATH  = os.getenv("ONNX_PATH", f"{MODEL_DIR}/onnx/model.onnx")
USE_L2NORM = os.getenv("USE_L2NORM", "true").lower() == "true"  # 默认对输出做 L2 归一化（若模型未归一）
WANTED_PROVIDERS = [x.strip() for x in os.getenv(
    "ORT_PROVIDERS",
    "CUDAExecutionProvider,CPUExecutionProvider"
).split(",")]

# =========================
# 工具函数
# =========================
def to_numpy(x, dtype=None):
    if isinstance(x, np.ndarray):
        return x.astype(dtype) if dtype is not None else x
    try:
        import torch
        if isinstance(x, torch.Tensor):
            x = x.detach().cpu().numpy()
            return x.astype(dtype) if dtype is not None else x
    except Exception:
        pass
    raise TypeError(f"Unsupported type for to_numpy: {type(x)}")

def l2norm(arr: np.ndarray, eps: float = 1e-9) -> np.ndarray:
    if arr.ndim == 1:
        n = np.linalg.norm(arr) + eps
        return arr / n
    n = np.linalg.norm(arr, axis=1, keepdims=True) + eps
    return arr / n

def decode_image_str(image_str: str) -> Image.Image:
    """
    支持三种输入：
      1) 本地路径：/path/to/xxx.jpg
      2) URL：     http(s)://...
      3) base64：  'data:image/...;base64,....' 或 纯 base64 字符串
    """
    # 本地路径
    if os.path.exists(image_str):
        img = Image.open(image_str)
        return img.convert("RGB") if img.mode != "RGB" else img

    # URL
    if image_str.startswith("http://") or image_str.startswith("https://"):
        try:
            resp = requests.get(image_str, timeout=10)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content))
            return img.convert("RGB") if img.mode != "RGB" else img
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"下载图片失败: {e}")

    # base64 (data:... 或 纯 base64)
    b64_str = image_str
    if image_str.startswith("data:image"):
        try:
            b64_str = image_str.split(",", 1)[1]
        except Exception:
            raise HTTPException(status_code=400, detail="data URL 解析失败")
    try:
        raw = base64.b64decode(b64_str, validate=True)
        img = Image.open(io.BytesIO(raw))
        return img.convert("RGB") if img.mode != "RGB" else img
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"base64 解码失败: {e}")

def select_providers() -> list:
    avail = set(ort.get_available_providers())
    selected = [p for p in WANTED_PROVIDERS if p in avail]
    if not selected:
        selected = ["CPUExecutionProvider"]
    return selected

# =========================
# 模型加载（与会话初始化）
# =========================
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)
image_processor = AutoImageProcessor.from_pretrained(MODEL_DIR, trust_remote_code=True)

providers = select_providers()
session = ort.InferenceSession(ONNX_PATH, providers=providers)
IN_METAS = {i.name: i for i in session.get_inputs()}
OUT_METAS = {o.name: o for o in session.get_outputs()}

# 解析输入名（兼容不同导出命名）
def resolve_input_names():
    input_names = {"input_ids": None, "attention_mask": None, "pixel": None}
    for name in IN_METAS.keys():
        lname = name.lower()
        if "input_ids" in lname and input_names["input_ids"] is None:
            input_names["input_ids"] = name
        if "attention_mask" in lname and input_names["attention_mask"] is None:
            input_names["attention_mask"] = name
        if ("pixel" in lname) or (lname in {"image", "images", "pixel_values", "pixel_values_image"}):
            input_names["pixel"] = name
    if input_names["input_ids"] is None:
        raise RuntimeError("无法找到 input_ids 的输入名，请检查 ONNX 输入。")
    if input_names["pixel"] is None:
        # 大多数模型都有像素输入；如果确实没有，image-only 就无法跑。
        # 这里不直接报错，等调用 image 分支时再报错更友好。
        pass
    return input_names

INPUT_NAMES = resolve_input_names()

def put_pixel(feed: dict, pixel_values: np.ndarray, pixel_input_name: str):
    """根据模型输入类型填充像素输入（tensor 或 sequence[tensor]）。"""
    meta = IN_METAS[pixel_input_name]
    t = meta.type.lower()
    if t.startswith("tensor("):
        feed[pixel_input_name] = pixel_values
    elif t.startswith("seq(") or t.startswith("sequence("):
        feed[pixel_input_name] = [pixel_values[b] for b in range(pixel_values.shape[0])]
    else:
        raise HTTPException(status_code=500, detail=f"不支持的像素输入类型: {meta.type}")

def pick_text_img_embeddings(ort_outputs: list, want_l2norm: bool):
    """
    兼容不同导出：尝试从输出中选出 text / image 的（优先取已归一化）。
    常见导出顺序：[text_unnorm, image_unnorm, text_norm, image_norm]
    Fallback：若无归一化输出，则对未归一化做 L2。
    """
    # 尝试通过输出名判断
    names = list(OUT_METAS.keys())
    text_emb = None
    image_emb = None

    def is_unit_norm(x: np.ndarray) -> bool:
        if x.ndim != 2:  # (B, D)
            return False
        norms = np.linalg.norm(x, axis=1)
        m = float(np.mean(norms))
        return 0.95 <= m <= 1.05  # 大致认为已经归一

    # 先通过名字找
    for i, name in enumerate(names):
        low = name.lower()
        if "text" in low and "emb" in low or "text_norm" in low:
            cand = ort_outputs[i]
            if text_emb is None or is_unit_norm(cand):
                text_emb = cand
        if "image" in low and "emb" in low or "image_norm" in low:
            cand = ort_outputs[i]
            if image_emb is None or is_unit_norm(cand):
                image_emb = cand

    # 名字判别失败时，用形状猜：找两个 (B, D) 且 B 分别等于文本批和图像批
    # 这里不完美，但够用；如果模型输出超过 2 个 (B,D)，优先后两个。
    if text_emb is None or image_emb is None:
        # 倒序找，很多导出里后两个是 norm 向量
        for arr in reversed(ort_outputs):
            if isinstance(arr, np.ndarray) and arr.ndim == 2:
                if text_emb is None:
                    text_emb = arr
                elif image_emb is None:
                    image_emb = arr
                if text_emb is not None and image_emb is not None:
                    break

    if text_emb is None or image_emb is None:
        # 兜底：取前两个 (B,D)
        found = [arr for arr in ort_outputs if isinstance(arr, np.ndarray) and arr.ndim == 2]
        if len(found) >= 2:
            text_emb, image_emb = found[:2]
        elif len(found) == 1:
            # 有可能是 text-only 或 image-only 情况（不常见）
            text_emb = found[0]
            image_emb = None
        else:
            raise HTTPException(status_code=500, detail="未在模型输出中找到 (B,D) 形状的向量。")

    # 归一化处理
    if want_l2norm:
        if text_emb is not None and not is_unit_norm(text_emb):
            text_emb = l2norm(text_emb)
        if image_emb is not None and not is_unit_norm(image_emb):
            image_emb = l2norm(image_emb)

    return text_emb, image_emb

def embed_texts(texts: list[str]) -> dict:
    t0 = time.time()
    tok = tokenizer(texts, padding=True, truncation=True, return_tensors="np")
    input_ids = tok["input_ids"].astype(np.int64)
    attention_mask = tok.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.astype(np.int64)

    # 若模型需要像素输入，也填一个“哑图像”（黑图）批，避免缺参报错
    feed = {}
    feed[INPUT_NAMES["input_ids"]] = input_ids
    if INPUT_NAMES["attention_mask"] and attention_mask is not None:
        feed[INPUT_NAMES["attention_mask"]] = attention_mask

    if INPUT_NAMES["pixel"] is not None:
        dummy = Image.new("RGB", (224, 224), (0, 0, 0))
        batch = [dummy] * len(texts)
        img_inputs = image_processor(batch, return_tensors="pt")
        pixel_values = to_numpy(img_inputs["pixel_values"], np.float32)
        put_pixel(feed, pixel_values, INPUT_NAMES["pixel"])

    outs = session.run(None, feed)
    text_emb, _ = pick_text_img_embeddings(outs, USE_L2NORM)
    elapsed = int((time.time() - t0) * 1000)
    return {"embeddings": text_emb.tolist(), "dims": int(text_emb.shape[1]), "timing_ms": elapsed}

def embed_images(images: list[Image.Image]) -> dict:
    t0 = time.time()
    img_inputs = image_processor(images, return_tensors="pt")  # 或改为 return_tensors="np"
    pixel_values = to_numpy(img_inputs["pixel_values"], np.float32)

    # 若模型需要文本输入，也填一个“哑文本”（空白）批，避免缺参报错
    dummy_texts = [""] * len(images)
    tok = tokenizer(dummy_texts, padding=True, truncation=True, return_tensors="np")
    input_ids = tok["input_ids"].astype(np.int64)
    attention_mask = tok.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.astype(np.int64)

    feed = {}
    feed[INPUT_NAMES["input_ids"]] = input_ids
    if INPUT_NAMES["attention_mask"] and attention_mask is not None:
        feed[INPUT_NAMES["attention_mask"]] = attention_mask
    if INPUT_NAMES["pixel"] is None:
        raise HTTPException(status_code=500, detail="该模型不包含像素输入，无法进行图像编码。")
    put_pixel(feed, pixel_values, INPUT_NAMES["pixel"])

    outs = session.run(None, feed)
    _, image_emb = pick_text_img_embeddings(outs, USE_L2NORM)
    elapsed = int((time.time() - t0) * 1000)
    return {"embeddings": image_emb.tolist(), "dims": int(image_emb.shape[1]), "timing_ms": elapsed}

def embed_pair(texts: list[str], images: list[Image.Image]) -> dict:
    if len(texts) != len(images):
        raise HTTPException(status_code=400, detail="texts 与 images 数量需一致（1:1 配对）。")
    t0 = time.time()

    # 文本
    tok = tokenizer(texts, padding=True, truncation=True, return_tensors="np")
    input_ids = tok["input_ids"].astype(np.int64)
    attention_mask = tok.get("attention_mask")
    if attention_mask is not None:
        attention_mask = attention_mask.astype(np.int64)

    # 图像
    img_inputs = image_processor(images, return_tensors="pt")
    pixel_values = to_numpy(img_inputs["pixel_values"], np.float32)

    # 组装 feed
    feed = {}
    feed[INPUT_NAMES["input_ids"]] = input_ids
    if INPUT_NAMES["attention_mask"] and attention_mask is not None:
        feed[INPUT_NAMES["attention_mask"]] = attention_mask
    if INPUT_NAMES["pixel"] is None:
        raise HTTPException(status_code=500, detail="该模型不包含像素输入，无法进行图像编码。")
    put_pixel(feed, pixel_values, INPUT_NAMES["pixel"])

    outs = session.run(None, feed)
    text_emb, image_emb = pick_text_img_embeddings(outs, USE_L2NORM)
    elapsed = int((time.time() - t0) * 1000)
    return {
        "text_embeddings": text_emb.tolist(),
        "image_embeddings": image_emb.tolist(),
        "dims": int(text_emb.shape[1]),
        "timing_ms": elapsed
    }

# =========================
# FastAPI 定义
# =========================
app = FastAPI(title="Jina-CLIP-V2 Embedding API", version="1.0.0")

# CORS（开发期放开，生产请收紧）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # 若前端带 cookie 再改 True
    allow_methods=["*"],
    allow_headers=["*"],
)

class PairRequest(BaseModel):
    text: str = Field(..., description="要编码的文本")
    image: str = Field(..., description="图片输入（本地路径 / URL / base64）")
    normalize: Optional[bool] = Field(default=True, description="是否对输出做 L2 归一（若模型已归一也安全）")

class TextRequest(BaseModel):
    text: str
    normalize: Optional[bool] = True

class ImageRequest(BaseModel):
    image: str
    normalize: Optional[bool] = True

@app.get("/health")
def health():
    return {
        "ok": True,
        "model_dir": MODEL_DIR,
        "onnx": os.path.exists(ONNX_PATH),
        "providers": providers,
        "inputs": list(IN_METAS.keys()),
        "outputs": list(OUT_METAS.keys()),
    }

@app.post("/v1/embed/pair")
def api_embed_pair(req: PairRequest):
    global USE_L2NORM
    prev = USE_L2NORM
    USE_L2NORM = bool(req.normalize)
    try:
        pil = decode_image_str(req.image)
        result = embed_pair([req.text], [pil])
        # 单样本时，降维成一维
        result["text_embedding"]  = result.pop("text_embeddings")[0]
        result["image_embedding"] = result.pop("image_embeddings")[0]
        result["model"] = "jina-clip-v2"
        return result
    finally:
        USE_L2NORM = prev  # 还原全局默认

@app.post("/v1/embed/text")
def api_embed_text(req: TextRequest):
    global USE_L2NORM
    prev = USE_L2NORM
    USE_L2NORM = bool(req.normalize)
    try:
        result = embed_texts([req.text])
        # 单样本时，降维成一维
        result["embedding"] = result.pop("embeddings")[0]
        result["model"] = "jina-clip-v2"
        return result
    finally:
        USE_L2NORM = prev

@app.post("/v1/embed/image")
def api_embed_image(req: ImageRequest):
    global USE_L2NORM
    prev = USE_L2NORM
    USE_L2NORM = bool(req.normalize)
    try:
        pil = decode_image_str(req.image)
        result = embed_images([pil])
        # 单样本时，降维成一维
        result["embedding"] = result.pop("embeddings")[0]
        result["model"] = "jina-clip-v2"
        return result
    finally:
        USE_L2NORM = prev

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "9108"))
    uvicorn.run("embed_api:app", host="0.0.0.0", port=port, reload=False)
