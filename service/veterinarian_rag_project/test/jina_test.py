# pip install transformers onnxruntime pillow
import os
import onnxruntime as ort
import numpy as np
from PIL import Image
from transformers import AutoImageProcessor, AutoTokenizer

MODEL_DIR = "/home/wmy/workspace/model_zoo/jinaai/jina-clip-v2"
ONNX_PATH = f"{MODEL_DIR}/onnx/model.onnx"

# 1) tokenizer & image_processor
tokenizer = AutoTokenizer.from_pretrained(MODEL_DIR, trust_remote_code=True)
image_processor = AutoImageProcessor.from_pretrained(MODEL_DIR, trust_remote_code=True)

# 2) 文本
sentences = [
    '浜辺に沈む美しい夕日',
    '해변 위로 아름다운 일몰',
]

# 3) 本地图片
image_paths = [
    '/home/wmy/workspace/data/beach1.jpg',
    '/home/wmy/workspace/data/beach2.jpg'
]

def load_local_image(path: str) -> Image.Image:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    img = Image.open(path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    return img

pil_images = [load_local_image(p) for p in image_paths]

# 4) tokenizer & processor -> numpy
tok = tokenizer(sentences, padding=True, truncation=True, return_tensors="np")
input_ids = tok["input_ids"].astype(np.int64)
attention_mask = tok.get("attention_mask")
if attention_mask is not None:
    attention_mask = attention_mask.astype(np.int64)


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

# 建议：这里直接让处理器返回 pt，再统一转 numpy，更稳定
img_inputs = image_processor(pil_images, return_tensors="pt")
pixel_values = to_numpy(img_inputs["pixel_values"], np.float32)

# 5) 创建 Session & 打印信息
providers_wanted = ["CUDAExecutionProvider", "CPUExecutionProvider"]
sess = ort.InferenceSession(ONNX_PATH, providers=providers_wanted)

print("Available providers:", ort.get_available_providers())
print("Session providers:", sess.get_providers())

in_metas = {i.name: i for i in sess.get_inputs()}
print("=== ONNX Inputs ===")
for i in sess.get_inputs():
    print(f"- name={i.name}, type={i.type}, shape={i.shape}")

def put_pixel_values(feed, name):
    """根据输入元信息，把 pixel_values 组装成 tensor 或 sequence[tensor]."""
    meta = in_metas[name]
    t = meta.type.lower()
    if t.startswith("tensor("):  # 普通张量: (B,3,H,W)
        feed[name] = pixel_values
    elif t.startswith("seq(") or t.startswith("sequence("):
        # 需要 sequence[tensor]：传入一个 list，每个元素是 (3,H,W) 的 np.float32
        feed[name] = [pixel_values[b] for b in range(pixel_values.shape[0])]
    else:
        raise TypeError(f"Unsupported pixel_values type: {meta.type}")

# 6) 组装 feed（按实际输入名来）
feed = {}

# input_ids / attention_mask 可能有不同命名，逐个兜底
for name in in_metas.keys():
    lname = name.lower()
    if "input_ids" in lname and "input_ids" not in feed:
        feed[name] = input_ids
    if attention_mask is not None and "attention_mask" in lname and "attention_mask" not in feed:
        feed[name] = attention_mask

# pixel_values 也可能叫别的名字，常见别名兜底
pixel_names = [n for n in in_metas.keys() if "pixel" in n.lower() or n.lower() in {"image", "images", "pixel_values_image"}]
if not pixel_names and "pixel_values" in in_metas:
    pixel_names = ["pixel_values"]
if not pixel_names:
    raise KeyError("找不到 pixel_values 的输入名，请打印上面的 ONNX Inputs 查看实际名称。")

# 只给一个像素输入名（大多数模型只有一个）
put_pixel_values(feed, pixel_names[0])

# 7) 运行
outputs = sess.run(None, feed)
print("Got outputs #:", len(outputs))
for idx, o in enumerate(outputs):
    print(f"out[{idx}] shape:", None if not hasattr(o, "shape") else o.shape)

# 如果输出顺序是 [text_unnorm, image_unnorm, text_norm, image_norm]
if len(outputs) >= 4:
    _, _, text_embeddings, image_embeddings = outputs[:4]
    print("text_embeddings:", text_embeddings.shape)
    print("image_embeddings:", image_embeddings.shape)
