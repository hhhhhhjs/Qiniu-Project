# recall_api.py
# FastAPI 召回服务：1) 图→info_msg  2) 文→图  3) 养护文→养护文本
import os
import time
import json
import requests
from typing import List, Optional, Dict, Any

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pymilvus import MilvusClient

# ===================== 配置 =====================
MILVUS_URI  = os.getenv("MILVUS_URI", "./petkb.db")              # Milvus Lite 本地文件
COLLECTION  = os.getenv("COLLECTION", "pet_knowledge_base")
EMBED_TXT   = os.getenv("EMBED_TXT", "http://127.0.0.1:9200/v1/embed/text")
EMBED_IMG   = os.getenv("EMBED_IMG", "http://127.0.0.1:9200/v1/embed/image")
TOPK_IMAGE  = int(os.getenv("TOPK_IMAGE", "8"))                   # 文搜图返回条数
TOPK_CARE   = int(os.getenv("TOPK_CARE", "6"))                    # 养护召回条数
ALPHA_IMAGE = float(os.getenv("ALPHA_IMAGE", "0.7"))              # 图像子库权重（图→品种融合）
SEARCH_PAR  = {"metric_type": "COSINE", "params": {}}             # AUTOINDEX + COSINE

# ===================== Milvus & HTTP 会话 =====================
client = MilvusClient(uri=MILVUS_URI)
http   = requests.Session()

# ===================== FastAPI 基础 =====================
app = FastAPI(title="Pet Recall API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=False,
)

# ===================== 模型 & 入参定义 =====================
class ImageRecallReq(BaseModel):
    image: str = Field(..., description="图片：本地路径/URL/base64（透传到你的 9200 接口）")
    topk_species: int = Field(5, ge=1, le=20, description="用于诊断输出的候选品种数（最终返回Top-1的info_msg）")

class Text2ImageReq(BaseModel):
    text: str = Field(..., description="文本查询，召回图片路径")
    topk: int = Field(TOPK_IMAGE, ge=1, le=50)

class CareRecallReq(BaseModel):
    text: str = Field(..., description="养护问题/关键词")
    topk: int = Field(TOPK_CARE, ge=1, le=20)
    species_hint: Optional[str] = Field(None, description="可选品种提示（species_id），若提供优先在该品种下检索")

# ===================== 工具函数 =====================
def _embed_text(q: str) -> List[float]:
    r = http.post(EMBED_TXT, json={"text": q, "normalize": True}, timeout=120)
    if not r.ok:
        raise HTTPException(500, f"embed text failed: {r.text}")
    return r.json()["embedding"]

def _embed_image(img: str) -> List[float]:
    r = http.post(EMBED_IMG, json={"image": img, "normalize": True}, timeout=120)
    if not r.ok:
        raise HTTPException(500, f"embed image failed: {r.text}")
    return r.json()["embedding"]

def _search(vec: List[float], expr: Optional[str], limit: int, fields: List[str]) -> List[Dict[str, Any]]:
    """MilvusClient.search 的返回在 2.5 里通常是 {'data':[...]} 或直接 list；做个兼容。"""
    res = client.search(
        collection_name=COLLECTION,
        data=[vec],
        filter=expr or "",
        limit=limit,
        output_fields=fields,
        search_params=SEARCH_PAR,
    )
    hits = res.get("data") if isinstance(res, dict) else res
    return hits or []

def _score(hit: Dict[str, Any]) -> float:
    # Milvus Lite + COSINE 通常 distance 越大越相似
    return float(hit.get("distance", hit.get("score", 0.0)))

def _field(hit: Dict[str, Any], name: str):
    # 有的返回嵌在 'entity'，有的平铺
    if "entity" in hit and isinstance(hit["entity"], dict):
        if name in hit["entity"]:
            return hit["entity"][name]
    return hit.get(name)

def _q(s: str) -> str:
    return s.replace('"', '\\"')

# ===================== 1) 图像 → info_msg =====================
@app.post("/v1/recall/by-image")
def recall_by_image(req: ImageRecallReq):
    t0 = time.time()
    qvec = _embed_image(req.image)

    # a) 图像子集
    hits_img = _search(
        qvec,
        expr='node_type == "image"',
        limit=max(50, req.topk_species * 10),
        fields=["species_id", "species_name", "node_type", "image_uri"],
    )

    # b) 文本子集（介绍文本）
    hits_intro = _search(
        qvec,
        expr='node_type == "introduction_text"',
        limit=max(30, req.topk_species * 6),
        fields=["species_id", "species_name", "node_type", "content"],
    )

    # c) 融合到物种
    score_map: Dict[str, float] = {}
    name_map: Dict[str, str] = {}
    for h in hits_img:
        sid = _field(h, "species_id")
        if not sid:
            continue
        name_map[sid] = _field(h, "species_name") or sid
        score_map[sid] = score_map.get(sid, 0.0) + ALPHA_IMAGE * _score(h)
    for h in hits_intro:
        sid = _field(h, "species_id")
        if not sid:
            continue
        name_map[sid] = _field(h, "species_name") or sid
        score_map[sid] = score_map.get(sid, 0.0) + (1.0 - ALPHA_IMAGE) * _score(h)

    if not score_map:
        raise HTTPException(404, "未召回到任何候选品种")

    # Top-1 作为预测品种
    fused_sorted = sorted(score_map.items(), key=lambda x: -x[1])[:req.topk_species]
    top_sid, top_score = fused_sorted[0]
    top_name = name_map.get(top_sid, top_sid)

    # d) 取 info_msg（introduction_text 最佳一条）
    hits_info = _search(
        qvec,  # 用同一 qvec 检 'introduction_text'，也可改成纯查询 species_id 的 query()
        expr=f'node_type == "introduction_text" and species_id == "{_q(top_sid)}"',
        limit=1,
        fields=["content", "species_id", "species_name"],
    )
    info_msg = _field(hits_info[0], "content") if hits_info else ""

    # e) 顺便给 Top-4 代表图（便于前端展示）
    hits_imgs_of_sid = _search(
        qvec,
        expr=f'node_type == "image" and species_id == "{_q(top_sid)}"',
        limit=4,
        fields=["image_uri", "species_id", "species_name"],
    )
    images = [
        {
            "image_uri": _field(h, "image_uri"),
            "score": round(_score(h), 6),
        } for h in hits_imgs_of_sid if _field(h, "image_uri")
    ]

    return {
        "species_id": top_sid,
        "species_name": top_name,
        "info_msg": info_msg,
        "images": images,
        "debug": {
            "candidates": [
                {"species_id": sid, "species_name": name_map.get(sid, sid), "score": round(sc, 6)}
                for sid, sc in fused_sorted
            ],
            "timing_ms": int((time.time() - t0) * 1000),
        }
    }

# ===================== 2) 文本 → 图片路径 =====================
@app.post("/v1/recall/by-text")
def recall_text2image(req: Text2ImageReq):
    t0 = time.time()
    qvec = _embed_text(req.text)
    hits = _search(
        qvec,
        expr='node_type == "image"',
        limit=req.topk,
        fields=["image_uri", "species_id", "species_name"],
    )
    items = []
    for h in hits:
        uri = _field(h, "image_uri")
        if not uri:
            continue
        items.append({
            "image_uri": uri,
            "species_id": _field(h, "species_id"),
            "species_name": _field(h, "species_name"),
            "score": round(_score(h), 6),
        })
    if not items:
        raise HTTPException(404, "未召回到图片")
    return {
        "results": items,
        "timing_ms": int((time.time() - t0) * 1000),
    }

# ===================== 3) 养护文 → 养护文本 =====================
@app.post("/v1/recall/care")
def recall_care(req: CareRecallReq):
    t0 = time.time()
    qvec = _embed_text(req.text)

    # 如果有 species_hint，优先限定；否则尝试先在 introduction_text 里估计品种
    species_expr = ""
    detected_sid = None
    if req.species_hint:
        detected_sid = req.species_hint
        species_expr = f' and species_id == "{_q(req.species_hint)}"'
    else:
        intro_hits = _search(
            qvec,
            expr='node_type == "introduction_text"',
            limit=3,
            fields=["species_id", "species_name"],
        )
        if intro_hits:
            detected_sid = _field(intro_hits[0], "species_id")
            species_expr = f' and species_id == "{_q(detected_sid)}"'

    hits = _search(
        qvec,
        expr='node_type == "care_text"' + species_expr,
        limit=req.topk,
        fields=["content", "tags", "species_id", "species_name"],
    )
    items = []
    for h in hits:
        items.append({
            "content": _field(h, "content"),
            "tags": _field(h, "tags"),
            "species_id": _field(h, "species_id"),
            "species_name": _field(h, "species_name"),
            "score": round(_score(h), 6),
        })
    if not items:
        # 退化为全局 care_text
        hits2 = _search(
            qvec,
            expr='node_type == "care_text"',
            limit=req.topk,
            fields=["content", "tags", "species_id", "species_name"],
        )
        for h in hits2:
            items.append({
                "content": _field(h, "content"),
                "tags": _field(h, "tags"),
                "species_id": _field(h, "species_id"),
                "species_name": _field(h, "species_name"),
                "score": round(_score(h), 6),
            })
    if not items:
        raise HTTPException(404, "未召回到养护文本")

    return {
        "species_detected": detected_sid,
        "results": items,
        "timing_ms": int((time.time() - t0) * 1000),
    }

# ===================== 健康检查 =====================
@app.get("/healthz")
def healthz():
    try:
        stats = client.describe_collection(COLLECTION)
    except Exception as e:
        raise HTTPException(500, f"Milvus error: {e}")
    return {"ok": True, "collection": COLLECTION, "stats": stats}
