# recall_api.py
import os
import time
from typing import Any, Dict, List, Optional, Literal, Tuple

import requests
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from pymilvus import MilvusClient

# ================== 配置（ENV 可覆盖） ==================
EMBED_API_URL = os.getenv("EMBED_API_URL", "http://127.0.0.1:9001/embed")

# Milvus / Milvus Lite：URI 可是文件路径（milvus-lite）或 http://host:19530
MILVUS_URI = os.getenv("MILVUS_DB_PATH", "/home/wmy/workspace/server/campus_rag_project/milvus_lite.db")
COLLECTION = os.getenv("MILVUS_COLLECTION", "jmu_pdf_pages_bge_m3")

# 检索参数
EMBED_DIM = int(os.getenv("EMBED_DIM", "1024"))
METRIC_TYPE = os.getenv("METRIC_TYPE", "COSINE")  # COSINE / IP / L2
DEFAULT_TOPK = int(os.getenv("DEFAULT_TOPK", "5"))
DEFAULT_MAX_LEN = int(os.getenv("DEFAULT_MAX_LEN", "512"))
DEFAULT_MIN_SIM = float(os.getenv("DEFAULT_MIN_SIM", "0.0"))  # 仅 COSINE 时直接按相似度阈值

# 请求超时
HTTP_TIMEOUT = float(os.getenv("HTTP_TIMEOUT", "10.0"))

# 输出字段（需与集合 schema 对齐）
DEFAULT_OUTPUT_FIELDS = os.getenv(
    "OUTPUT_FIELDS",
    "id,source,page_no,title,text,summary,path_txt"
).split(",")

# ================== FastAPI ==================
app = FastAPI(title="Campus Assistant Recall API", version="1.0.1")

# ================== Schemas ==================
class RecallQueryOption(BaseModel):
    return_summary: bool = False
    top_k: int = DEFAULT_TOPK
    max_length: int = DEFAULT_MAX_LEN
    min_score: float = DEFAULT_MIN_SIM
    source_filter: Optional[str] = None            # e.g. "集美大学2025新生手册.pdf"
    output_fields: Optional[List[str]] = None      # 覆盖默认输出字段

class RecallQuery(BaseModel):
    text: str = Field(..., min_length=1, description="已去口语化的查询文本")
    options: RecallQueryOption = RecallQueryOption()

class HitItem(BaseModel):
    rank: int
    score_raw: Optional[float] = None
    score_cosine: Optional[float] = None
    entity: Dict[str, Any]  # 透传 Milvus 字段，并附加 _content/_content_type

class RecallResult(BaseModel):
    query: str
    topk: int
    used_filter: Optional[str] = None
    elapsed_ms: int
    hits: List[HitItem]

class RecallBatchRequest(BaseModel):
    queries: List[RecallQuery]

class RecallBatchResponse(BaseModel):
    results: List[RecallResult]

# ================== Utils ==================
def _l2_normalize(arr: np.ndarray) -> np.ndarray:
    if arr.ndim == 1:
        arr = arr[None, :]
    norms = np.linalg.norm(arr, axis=1, keepdims=True) + 1e-12
    return arr / norms

def _safe_score(hit: dict, metric_type: str) -> Tuple[Optional[float], Optional[float]]:
    """
    返回 (raw, cosine_sim)
    - 有些 SDK 返回 hit['score']（已是相似度：越大越相似）
    - 有些返回 hit['distance']（COSINE 下通常是 1 - cos_sim）
    """
    raw = hit.get("score", None)
    if raw is not None:
        return float(raw), float(raw)
    dist = hit.get("distance", None)
    if dist is None:
        return None, None
    if metric_type.upper() == "COSINE":
        return float(dist), 1.0 - float(dist)
    return float(dist), None

def _build_filter(source_filter: Optional[str]) -> Optional[str]:
    if not source_filter:
        return None
    sf = source_filter.replace('"', '\\"')
    return f'source == "{sf}"'

def _embed(texts: List[str], max_length: int, normalize: bool = True) -> np.ndarray:
    """
    调 BGE Embedding Service；若失败抛 HTTPException。
    """
    try:
        r = requests.post(
            EMBED_API_URL,
            json={"texts": texts, "normalize": normalize, "max_length": max_length},
            timeout=HTTP_TIMEOUT,
        )
        r.raise_for_status()
        data = r.json()
        vecs = np.array(data.get("embeddings", []), dtype=np.float32)
        if vecs.ndim == 1:
            vecs = vecs[None, :]
        if vecs.shape[1] != EMBED_DIM:
            raise RuntimeError(f"Embedding dim mismatch: got {vecs.shape[1]} expect {EMBED_DIM}")
        return vecs
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Embed service failed: {e}")

def _ensure_milvus() -> MilvusClient:
    try:
        client = MilvusClient(MILVUS_URI)
        if not client.has_collection(COLLECTION):
            raise RuntimeError(f"Collection not found: {COLLECTION}")
        client.load_collection(COLLECTION)
        return client
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Milvus connect/load failed: {e}")

# ================== 核心：单条查询 ==================
def _do_recall_once(client: MilvusClient, q: RecallQuery) -> RecallResult:
    t0 = time.time()

    # 1) 向量化（输入已去口语化，不再调用外部清洗）
    vec = _embed([q.text], q.options.max_length, normalize=True)[0].tolist()

    # 2) 过滤表达式
    expr = _build_filter(q.options.source_filter)

    # 3) Milvus 检索
    search_params = {"metric_type": METRIC_TYPE}
    out_fields = q.options.output_fields or DEFAULT_OUTPUT_FIELDS
    try:
        res = client.search(
            collection_name=COLLECTION,
            data=[vec],
            limit=q.options.top_k,
            output_fields=out_fields,
            search_params=search_params,
            filter=expr  # 如果你的 pymilvus 版本用 expr=expr，请改这里
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Milvus search failed: {e}")

    hits = res[0] if res else []
    items: List[HitItem] = []

    # 4) 组装输出 + 阈值过滤
    for _idx, hit in enumerate(hits, start=1):
        raw, cos = _safe_score(hit, METRIC_TYPE)
        if q.options.min_score > 0:
            cmp_score = cos if cos is not None else (raw if raw is not None else 0.0)
            if cmp_score < q.options.min_score:
                continue

        ent = hit.get("entity", {})
        if q.options.return_summary and ent.get("summary"):
            ent["_content"] = ent["summary"]
            ent["_content_type"] = "summary"
        else:
            ent["_content"] = ent.get("text")
            ent["_content_type"] = "text"

        items.append(HitItem(
            rank=len(items) + 1,
            score_raw=raw,
            score_cosine=cos,
            entity=ent
        ))

    return RecallResult(
        query=q.text,
        topk=q.options.top_k,
        used_filter=expr,
        elapsed_ms=int((time.time() - t0) * 1000),
        hits=items
    )

# ================== 批量召回 ==================
@app.post("/v1/recall", response_model=RecallBatchResponse)
def recall(req: RecallBatchRequest):
    if not req.queries:
        raise HTTPException(status_code=400, detail="queries 不能为空")
    client = _ensure_milvus()
    results = [_do_recall_once(client, q) for q in req.queries]
    return RecallBatchResponse(results=results)

@app.get("/healthz")
def healthz():
    status = "ok"
    detail = {"milvus": None, "embed_api": None}

    try:
        _ = _ensure_milvus()
        detail["milvus"] = "ok"
    except Exception as e:
        status = "degraded"
        detail["milvus"] = f"error: {e}"

    try:
        r = requests.get(EMBED_API_URL.replace("/embed", "/healthz"), timeout=3)
        detail["embed_api"] = r.json() if r.ok else f"http {r.status_code}"
        if not r.ok:
            status = "degraded"
    except Exception as e:
        status = "degraded"
        detail["embed_api"] = f"error: {e}"

    return {"status": status, "detail": detail}
