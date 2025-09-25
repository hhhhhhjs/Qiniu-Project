import os
import time
import queue
import threading
from typing import List, Optional, Dict, Any

import numpy as np
from fastapi import FastAPI, Body, HTTPException
from pydantic import BaseModel
from FlagEmbedding import BGEM3FlagModel
import uvicorn
from functools import lru_cache

# ------------------- 可调参数 -------------------
MODEL_PATH = os.getenv("BGE_MODEL_PATH", "/home/wmy/workspace/model_zoo/BAAI/bge-m3")
USE_FP16 = os.getenv("BGE_USE_FP16", "true").lower() == "true"
MAX_LENGTH = int(os.getenv("BGE_MAX_LENGTH", "4096"))
EMBED_DIM = 1024

# 微批参数
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "64"))
MAX_WAIT_MS = int(os.getenv("MAX_WAIT_MS", "8"))       # 等待聚合的最大毫秒
WORKER_THREADS = int(os.getenv("WORKER_THREADS", "1")) # 一般=1，避免多次占用同一GPU
# ------------------------------------------------

app = FastAPI(title="BGE Embedding Service", version="1.1.0")

class EmbedRequest(BaseModel):
    texts: List[str]
    normalize: bool = True
    max_length: Optional[int] = None

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    dim: int
    elapsed_ms: int

class RerankRequest(BaseModel):
    query: str
    documents: List[str]
    top_k: Optional[int] = None
    max_length: Optional[int] = None
    normalize: bool = True  # 用于是否对向量做L2归一化后再计算cos相似

class RerankItem(BaseModel):
    index: int
    document: str
    score: float

class RerankResponse(BaseModel):
    results: List[RerankItem]
    elapsed_ms: int

# 全局：模型与锁
bge = BGEM3FlagModel(
    MODEL_PATH,
    use_fp16=USE_FP16,
    normalize_embeddings=False  # 手动归一化更可控
)
print(f"[ok] BGE model loaded from {MODEL_PATH}")

MODEL_LOCK = threading.Lock()  # 统一串行化 GPU 推理，避免多线程竞争

def _l2_normalize(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 1:
        arr = arr[None, :]
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr / norms

@lru_cache(maxsize=8192)
def _cache_key(text: str, max_len: int) -> bytes:
    return f"{max_len}::{text}".encode("utf-8")

# 请求与结果的桥接（/embed 用微批）
class Task:
    def __init__(self, texts: List[str], max_length: int, normalize: bool):
        self.texts = texts
        self.max_length = max_length
        self.normalize = normalize
        self.result: Optional[List[List[float]]] = None
        self.evt = threading.Event()

request_q: "queue.Queue[Task]" = queue.Queue(maxsize=2048)

def _encode_texts(texts: List[str], max_length: int) -> np.ndarray:
    """对外统一的编码函数：内部加锁保证与其他路由串行访问模型。"""
    with MODEL_LOCK:
        out = bge.encode(texts, batch_size=min(64, len(texts)), max_length=max_length)
    dense = out["dense_vecs"]
    if isinstance(dense, list):
        dense = np.array(dense, dtype=np.float32)
    else:
        dense = dense.astype(np.float32)
    return dense

def worker_loop(worker_id: int):
    while True:
        batch: List[Task] = []
        try:
            first: Task = request_q.get()
            batch = [first]
            t0 = time.time()
            # 叠批：尽量在 MAX_WAIT_MS 内凑到较大的 batch
            while (len(batch) < MAX_BATCH_SIZE) and ((time.time() - t0) * 1000 < MAX_WAIT_MS):
                try:
                    nxt = request_q.get_nowait()
                    batch.append(nxt)
                except queue.Empty:
                    time.sleep(0.001)
                    break

            # 整理输入
            all_texts: List[str] = []
            max_lengths: List[int] = []
            norms: List[bool] = []
            for t in batch:
                all_texts.extend(t.texts)
                max_lengths.extend([t.max_length] * len(t.texts))
                norms.append(t.normalize)

            used_max_len = min(max_lengths) if max_lengths else MAX_LENGTH
            dense = _encode_texts(all_texts, used_max_len)

            # 统一归一化：只要批里有任何任务要求 normalize=True，就对整体做归一化
            if any(norms):
                dense = _l2_normalize(dense).astype(np.float32)

            # 切回给各 task
            offset = 0
            for t in batch:
                n = len(t.texts)
                vecs = dense[offset:offset+n]
                offset += n
                t.result = vecs.tolist()
                t.evt.set()

        except Exception as e:
            # 确保异常也能唤醒等待方
            for t in batch:
                if t and not t.evt.is_set():
                    t.result = []
                    t.evt.set()
            print(f"[worker-{worker_id}] error: {e}")

# 启动 worker
for i in range(WORKER_THREADS):
    th = threading.Thread(target=worker_loop, args=(i,), daemon=True)
    th.start()
    print(f"[ok] worker {i} started")

@app.get("/healthz")
def healthz():
    return {"status": "ok", "model": "BGE-M3", "dim": EMBED_DIM}

@app.post("/embed", response_model=EmbedResponse)
def embed(req: EmbedRequest):
    t0 = time.time()
    if not req.texts:
        return EmbedResponse(embeddings=[], dim=EMBED_DIM, elapsed_ms=int((time.time()-t0)*1000))

    max_len = req.max_length or MAX_LENGTH

    # 单条用 LRU 缓存（演示简化），批量建议自行实现批缓存
    if len(req.texts) == 1:
        key = _cache_key(req.texts[0], max_len)

        @lru_cache(maxsize=8192)
        def _single_cached(_key: bytes, text: str, max_len: int, normalize: bool):
            dense = _encode_texts([text], max_len)
            if normalize:
                dense = _l2_normalize(dense).astype(np.float32)
            return dense[0].tolist()

        vec = _single_cached(key, req.texts[0], max_len, req.normalize)
        return EmbedResponse(embeddings=[vec], dim=EMBED_DIM, elapsed_ms=int((time.time()-t0)*1000))

    # 入队等待 worker 合并
    task = Task(req.texts, max_len, req.normalize)
    request_q.put(task)
    ok = task.evt.wait(timeout=30.0)  # 超时可调
    if not ok or task.result is None:
        return EmbedResponse(embeddings=[], dim=EMBED_DIM, elapsed_ms=int((time.time()-t0)*1000))
    return EmbedResponse(embeddings=task.result, dim=EMBED_DIM, elapsed_ms=int((time.time()-t0)*1000))

@app.post("/rerank", response_model=RerankResponse)
def rerank(req: RerankRequest):
    t0 = time.time()
    if not req.query:
        raise HTTPException(status_code=400, detail="query is empty")
    if not req.documents:
        return RerankResponse(results=[], elapsed_ms=int((time.time()-t0)*1000))

    max_len = req.max_length or MAX_LENGTH

    # 编码 query 与 documents
    q_vec = _encode_texts([req.query], max_len)[0]  # (D,)
    d_vecs = _encode_texts(req.documents, max_len)  # (N, D)

    # 归一化 + 余弦相似度
    if req.normalize:
        q_vec = _l2_normalize(q_vec).astype(np.float32)[0]
        d_vecs = _l2_normalize(d_vecs).astype(np.float32)

    # 计算分数：cos = q · d
    scores = (d_vecs @ q_vec.astype(np.float32))  # (N,)
    idx = np.argsort(-scores)  # 降序
    if req.top_k:
        idx = idx[:req.top_k]

    results = [
        RerankItem(index=int(i), document=req.documents[int(i)], score=float(scores[int(i)]))
        for i in idx
    ]
    return RerankResponse(results=results, elapsed_ms=int((time.time()-t0)*1000))

if __name__ == "__main__":
    # 单进程单实例占用一张 GPU；多卡请起多个进程并设置 CUDA_VISIBLE_DEVICES 亲和
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
