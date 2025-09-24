import os
import time
import queue
import threading
from typing import List, Optional, Dict, Any

import numpy as np
from fastapi import FastAPI, Body
from pydantic import BaseModel
from FlagEmbedding import BGEM3FlagModel
import uvicorn

# ------------------- 可调参数 -------------------
MODEL_PATH = os.getenv("BGE_MODEL_PATH", "/home/yaf/workspace/model_zoo/BAAI/bge-m3")
USE_FP16 = os.getenv("BGE_USE_FP16", "true").lower() == "true"
MAX_LENGTH = int(os.getenv("BGE_MAX_LENGTH", "4096"))
EMBED_DIM = 1024

# 微批参数
MAX_BATCH_SIZE = int(os.getenv("MAX_BATCH_SIZE", "64"))
MAX_WAIT_MS = int(os.getenv("MAX_WAIT_MS", "8"))      # 等待聚合的最大毫秒
WORKER_THREADS = int(os.getenv("WORKER_THREADS", "1"))  # 一般=1，避免多次占用同一GPU
# ------------------------------------------------

app = FastAPI(title="BGE Embedding Service", version="1.0.0")

class EmbedRequest(BaseModel):
    texts: List[str]
    normalize: bool = True
    max_length: Optional[int] = None

class EmbedResponse(BaseModel):
    embeddings: List[List[float]]
    dim: int
    elapsed_ms: int

# 全局：模型与队列
bge = BGEM3FlagModel(
    MODEL_PATH,
    use_fp16=USE_FP16,
    normalize_embeddings=False  # 手动归一化更可控
)
print(f"[ok] BGE model loaded from {MODEL_PATH}")

# 简单 LRU 缓存（可换成 Redis/Memcached）
from functools import lru_cache

def _l2_normalize(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 1:
        arr = arr[None, :]
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr / norms

@lru_cache(maxsize=8192)
def _cache_key(text: str, max_len: int) -> bytes:
    # 只缓存 key；真正缓存内容由 lru_cache 包装函数完成
    return f"{max_len}::{text}".encode("utf-8")

# 请求与结果的桥接
class Task:
    def __init__(self, texts: List[str], max_length: int, normalize: bool):
        self.texts = texts
        self.max_length = max_length
        self.normalize = normalize
        self.result: Optional[List[List[float]]] = None
        self.evt = threading.Event()

request_q: "queue.Queue[Task]" = queue.Queue(maxsize=2048)

def worker_loop(worker_id: int):
    while True:
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

            # 这里用同一个 max_length（取批内最小/最大都可；我们取最小，避免截断差异）
            used_max_len = min(max_lengths) if max_lengths else MAX_LENGTH
            out = bge.encode(all_texts, batch_size=min(64, len(all_texts)), max_length=used_max_len)
            dense = out["dense_vecs"]
            if isinstance(dense, list):
                dense = np.array(dense, dtype=np.float32)

            # 统一归一化选项：只要批里有任何任务要求 normalize=True，就归一化整体，再对不需要的原样返回也无妨
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

    # 命中缓存的直接返回（逐条；也可以做批量缓存）
    # 注意：这里为了演示简单，只缓存单条；更好的做法是自己实现批量缓存
    if len(req.texts) == 1:
        key = _cache_key(req.texts[0], max_len)
        @lru_cache(maxsize=8192)
        def _single_cached(_key: bytes, text: str, max_len: int, normalize: bool):
            out = bge.encode([text], batch_size=1, max_length=max_len)
            dense = out["dense_vecs"]
            if isinstance(dense, list):
                dense = np.array(dense, dtype=np.float32)
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

if __name__ == "__main__":
    # 单进程单实例占用一张 GPU；多卡请起多个进程并设置 CUDA_VISIBLE_DEVICES 亲和
    uvicorn.run(app, host="0.0.0.0", port=8000, workers=1)
