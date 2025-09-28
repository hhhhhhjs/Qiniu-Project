#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import io
import time
import json
import base64
from typing import Optional, Dict, Any, List

import requests
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ===================== 环境变量 =====================
INTENT_API_URL   = os.getenv("INTENT_API_URL",   "http://127.0.0.1:9101/v1/intent")
RECALL_BASE_URL  = os.getenv("RECALL_BASE_URL",  "http://127.0.0.1:9102")  # 下面拼接具体 path
ROLEPLAY_API_URL = os.getenv("ROLEPLAY_API_URL", "http://127.0.0.1:9103/v1/roleplay/stream")

# 文搜图
RECALL_TEXT2IMG_URL = f"{RECALL_BASE_URL}/v1/recall/by-text"
# 养护召回
RECALL_CARE_URL     = f"{RECALL_BASE_URL}/v1/recall/care"

# 其他可调
DEFAULT_TOPK_IMAGES = int(os.getenv("TOPK_IMAGES", "4"))
DEFAULT_TOPK_CARE   = int(os.getenv("TOPK_CARE",   "6"))
HTTP_TIMEOUT_SEC    = float(os.getenv("HTTP_TIMEOUT", "30"))

# ===================== FastAPI 基础 =====================
app = FastAPI(title="Pet Workflow API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,        # 前端不带 cookie，建议 False
    allow_methods=["*"],
    allow_headers=["*"],
)

http = requests.Session()

# ===================== I/O 模型 =====================
class WorkflowTextReq(BaseModel):
    text: str = Field(..., description="用户输入文本")
    lang_hint: Optional[str] = Field(None, description="语言提示，如 zh/en")
    topk_images: int = Field(DEFAULT_TOPK_IMAGES, ge=1, le=20, description="文搜图返回张数")
    topk_care: int   = Field(DEFAULT_TOPK_CARE,   ge=1, le=20, description="养护召回条数")
    # 遇到非 by-text / by-image 情况，统一 fallback 到 care
    force_care_on_unknown: bool = Field(True, description="非文搜图/图搜文一律按 care")

class ImageItem(BaseModel):
    image_uri: str
    image_b64: Optional[str] = None
    score: Optional[float] = None
    species_id: Optional[str] = None
    species_name: Optional[str] = None

class WorkflowResp(BaseModel):
    route: str = Field(..., description="'by-text' or 'care'")
    intent: Dict[str, Any]
    result_text: Optional[str] = None
    images: Optional[List[ImageItem]] = None
    recall_items: Optional[List[Dict[str, Any]]] = None
    timing_ms: int

# ===================== 小工具 =====================
def _is_url(u: str) -> bool:
    return u.startswith("http://") or u.startswith("https://")

def _is_data_uri(u: str) -> bool:
    return u.startswith("data:image/")

def _to_b64_from_uri(uri: str) -> Optional[str]:
    """
    将 image_uri 转为 base64（不带 data: 前缀，只给纯 base64 字符串）
    支持：本地文件路径 / http(s) URL / data:image/*;base64,xxx
    """
    try:
        # 1) 已经是 data URI
        if _is_data_uri(uri):
            # data:image/png;base64,xxxx
            comma = uri.find(",")
            if comma >= 0:
                return uri[comma + 1:]
            return None

        # 2) http(s) URL
        if _is_url(uri):
            r = http.get(uri, timeout=HTTP_TIMEOUT_SEC)
            if not r.ok:
                return None
            raw = r.content
            return base64.b64encode(raw).decode("utf-8")

        # 3) 本地文件
        if os.path.exists(uri) and os.path.isfile(uri):
            with open(uri, "rb") as f:
                raw = f.read()
            return base64.b64encode(raw).decode("utf-8")

        # 其他情况（如 MinIO 路径等），可在此扩展
        return None
    except Exception:
        return None

def _call_intent(text: str, lang_hint: Optional[str]) -> Dict[str, Any]:
    payload = {"query": text, "has_image": False, "lang_hint": lang_hint or ""}
    r = http.post(INTENT_API_URL, json=payload, timeout=HTTP_TIMEOUT_SEC)
    if not r.ok:
        raise HTTPException(status_code=502, detail=f"intent error: {r.text}")
    return r.json()

def _call_recall_text2img(text: str, topk: int) -> List[Dict[str, Any]]:
    payload = {"text": text, "topk": topk}
    r = http.post(RECALL_TEXT2IMG_URL, json=payload, timeout=HTTP_TIMEOUT_SEC)
    if r.status_code == 404:
        return []
    if not r.ok:
        raise HTTPException(status_code=502, detail=f"recall(by-text) error: {r.text}")
    data = r.json()
    return data.get("results", [])

def _call_recall_care(text: str, topk: int) -> Dict[str, Any]:
    payload = {"text": text, "topk": topk}
    r = http.post(RECALL_CARE_URL, json=payload, timeout=HTTP_TIMEOUT_SEC)
    if not r.ok:
        raise HTTPException(status_code=502, detail=f"recall(care) error: {r.text}")
    return r.json()

def _call_roleplay_stream(user_query: str, retrieved_text: str) -> str:
    """
    连接你已有的 /v1/roleplay/stream（SSE），聚合增量，返回完整文本。
    约定：服务端以 `data: {"delta":"..."}` 逐块输出，结束时 `data: [DONE]`
    """
    payload = {"user_query": user_query, "retrieved_text": retrieved_text}
    with http.post(ROLEPLAY_API_URL, json=payload, stream=True, timeout=HTTP_TIMEOUT_SEC) as r:
        if r.status_code != 200:
            # 有些错误会用 SSE 的 error 事件，这里直接报
            raise HTTPException(status_code=502, detail=f"roleplay stream error: {r.text}")

        chunks: List[str] = []
        for raw_line in r.iter_lines(decode_unicode=True):
            if not raw_line:
                continue
            # 仅解析以 "data:" 开头的行
            if raw_line.startswith("data:"):
                content = raw_line[5:].strip()
                if content == "[DONE]":
                    break
                try:
                    obj = json.loads(content)
                    delta = obj.get("delta")
                    if delta:
                        chunks.append(delta)
                except Exception:
                    # 允许服务端偶尔发非 JSON 文本
                    if content and content != "[DONE]":
                        chunks.append(content)
        return "".join(chunks).strip()

# ===================== 工作流主路由 =====================
@app.post("/v1/workflow/route", response_model=WorkflowResp)
def workflow_route(req: WorkflowTextReq = Body(...)):
    t0 = time.time()

    # 1) 意图识别
    intent = _call_intent(req.text, req.lang_hint)

    action = str(intent.get("action", "care"))  # 只会是 by-text / by-image / care
    # 你的规则：非文搜图/图搜文，一律 care
    if action not in ("by-text", "by-image"):
        action = "care"
    elif action == "by-image" and req.force_care_on_unknown:
        # 当前工作流仅处理文本输入，若意图判断为“图搜文”，也统一走 care
        action = "care"

    # 2) 分支：文搜图 or care
    if action == "by-text":
        hits = _call_recall_text2img(req.text, req.topk_images)
        images: List[Dict[str, Any]] = []
        for h in hits:
            uri = h.get("image_uri")
            b64 = _to_b64_from_uri(uri) if uri else None
            images.append({
                "image_uri": uri,
                "image_b64": b64,
                "score": h.get("score"),
                "species_id": h.get("species_id"),
                "species_name": h.get("species_name"),
            })

        if not images:
            # 文搜图没结果，兜底到 care 流程
            care = _call_recall_care(req.text, req.topk_care)
            retrieved_text = "\n\n---\n\n".join(
                [it.get("content", "") for it in care.get("results", []) if it.get("content")]
            )[:8000] or "（召回为空）"
            final_text = _call_roleplay_stream(req.text, retrieved_text)
            return WorkflowResp(
                route="care",
                intent=intent,
                result_text=final_text,
                recall_items=care.get("results", []),
                timing_ms=int((time.time() - t0) * 1000),
            )

        return WorkflowResp(
            route="by-text",
            intent=intent,
            images=[ImageItem(**it) for it in images],
            timing_ms=int((time.time() - t0) * 1000),
        )

    # —— care 路径 ——
    care = _call_recall_care(req.text, req.topk_care)
    retrieved_text = "\n\n---\n\n".join(
        [it.get("content", "") for it in care.get("results", []) if it.get("content")]
    )[:8000] or "（召回为空）"
    final_text = _call_roleplay_stream(req.text, retrieved_text)

    return WorkflowResp(
        route="care",
        intent=intent,
        result_text=final_text,
        recall_items=care.get("results", []),
        timing_ms=int((time.time() - t0) * 1000),
    )

# ===================== 健康检查 =====================
@app.get("/healthz")
def healthz():
    return {
        "ok": True,
        "intent_api": INTENT_API_URL,
        "recall_text2img": RECALL_TEXT2IMG_URL,
        "recall_care": RECALL_CARE_URL,
        "roleplay_stream": ROLEPLAY_API_URL,
    }
