# app.py
import os
import uvicorn
import time
import json
import logging
from contextlib import contextmanager
from fastapi import FastAPI, Body, HTTPException, Path, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List, Generator
from datetime import datetime
from uuid import uuid4
from threading import Lock

# pip install zhipuai fastapi uvicorn
from zhipuai import ZhipuAI

# ============ Logging ============
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("timing")

# ============ Config ============
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
MODEL_NAME = os.getenv("ZHIPUAI_MODEL", "glm-4.5")
APP_PORT = int(os.getenv("PORT", "9003"))

# 对话历史保留的最大轮数（user+assistant 为一轮）
MAX_TURNS = int(os.getenv("MAX_TURNS", "12"))
DEFAULT_TEMPERATURE = float(os.getenv("TEMP", "0.2"))
DEFAULT_MAX_TOKENS = int(os.getenv("MAX_TOKENS", "512"))

if not ZHIPUAI_API_KEY:
    raise RuntimeError("请先设置环境变量 ZHIPUAI_API_KEY")

client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
app = FastAPI(title="JMU 迎新助手·小美（RAG+Multi-Turn）", version="1.1.0")

# ============ Timing Helper ============
class Timer:
    def __init__(self) -> None:
        self._t0 = time.perf_counter()
        self.spans: Dict[str, float] = {}

    @contextmanager
    def span(self, name: str):
        s = time.perf_counter()
        try:
            yield
        finally:
            self.spans[name] = round((time.perf_counter() - s) * 1000, 3)

    def done(self) -> float:
        return round((time.perf_counter() - self._t0) * 1000, 3)

# ============ Prompt ============
SYSTEM_PROMPT = """你是“集美大学迎新助手”的虚拟数字人“小美”，一位青春活力、亲切耐心的女学姐。
职责：基于学校官方资料（招生手册、新生入学手册等）和 RAG 召回片段，准确、清晰地回答新生问题。

【口吻】温暖、积极、学姐风；不能使用任何表情符号。
【风格】结构化分点表达；重要数字/日期/地点加粗。
【规则】
1) 仅使用用户问题与召回文本中的信息，不要编造。
2) 若召回文本无答案，说明“暂未查到”，并给出合理的下一步建议（如联系学院/招办/官网查询）。
3) 生活类问题可补充贴心提醒，但不得虚构。
4) 输出中文。
"""

# ============ Session Store (in-memory) ============
sessions: Dict[str, Dict[str, Any]] = {}
lock = Lock()

# ============ Schemas ============
class RagRequest(BaseModel):
    query: str = Field(..., description="用户问题")
    retrieved_text: str = Field(..., description="RAG召回的文本（可拼接多段）")
    meta: Optional[Dict[str, Any]] = Field(default=None, description="可选的元数据")
    temperature: float = Field(DEFAULT_TEMPERATURE, ge=0.0, le=1.0, description="采样温度")
    max_tokens: int = Field(DEFAULT_MAX_TOKENS, ge=1, le=4096, description="最大生成长度")

class RagResponse(BaseModel):
    answer: str
    model: str
    created: str
    usage: Optional[Dict[str, Any]] = None
    meta: Optional[Dict[str, Any]] = None
    session_id: Optional[str] = None

class CreateSessionRequest(BaseModel):
    system_prompt: Optional[str] = Field(None, description="可选覆盖默认小美系统提示词")

class CreateSessionResponse(BaseModel):
    session_id: str
    created: str

class ChatRequest(BaseModel):
    session_id: Optional[str] = Field(None, description="会话ID；若为空将自动创建新会话")
    query: str = Field(..., description="用户问题")
    retrieved_text: str = Field("", description="RAG召回文本（建议每轮传入当轮召回）")
    temperature: float = Field(DEFAULT_TEMPERATURE, ge=0.0, le=1.0)
    max_tokens: int = Field(DEFAULT_MAX_TOKENS, ge=1, le=4096)
    meta: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    session_id: str
    answer: str
    model: str
    created: str
    usage: Optional[Dict[str, Any]] = None
    turn_index: int
    meta: Optional[Dict[str, Any]] = None

class SessionDump(BaseModel):
    session_id: str
    created: str
    updated: str
    messages: List[Dict[str, str]]

# ============ Helpers ============
def _now_iso() -> str:
    return datetime.utcnow().isoformat()

def _new_session_id() -> str:
    return uuid4().hex

def _init_session(system_prompt: Optional[str] = None) -> str:
    sid = _new_session_id()
    with lock:
        sessions[sid] = {
            "created": _now_iso(),
            "updated": _now_iso(),
            "messages": [
                {"role": "system", "content": system_prompt or SYSTEM_PROMPT}
            ],
            "thinking": {"type": "disabled"},
        }
    return sid

def _append_and_trim(sid: str, role: str, content: str) -> None:
    sess = sessions.get(sid)
    if not sess:
        raise KeyError("会话不存在")
    sess["messages"].append({"role": role, "content": content})
    msgs = sess["messages"]
    system_msg = msgs[0] if msgs and msgs[0]["role"] == "system" else {"role": "system", "content": SYSTEM_PROMPT}
    tail = [m for m in msgs[1:]][-2*MAX_TURNS:]
    sess["messages"] = [system_msg] + tail
    sess["updated"] = _now_iso()

def _build_user_payload(query: str, retrieved_text: str) -> str:
    if not retrieved_text.strip():
        retrieved_text = "（未检索到相关官方条目）"
    return (
        "【用户问题】\n"
        f"{query}\n\n"
        "【召回文本】\n"
        f"{retrieved_text}\n\n"
        "【请用“小美”的口吻作答】："
    )

def _call_zhipu(messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int) -> Dict[str, Any]:
    # 同步（非流式）调用
    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return resp

def _call_zhipu_stream(messages: List[Dict[str, str]], model: str, temperature: float, max_tokens: int):
    # 流式调用
    stream = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
    )
    return stream

def _extract_answer_and_usage(resp: Any) -> (str, Optional[Dict[str, Any]]):
    try:
        choice = resp.choices[0] if hasattr(resp, "choices") else resp["choices"][0]
        if hasattr(choice, "message"):
            answer = getattr(choice.message, "content", None)
        else:
            # dict-like
            answer = choice.get("message", {}).get("content")
    except Exception:
        answer = None

    if not answer:
        answer = str(resp)

    usage = None
    if hasattr(resp, "usage"):
        usage = {
            "prompt_tokens": getattr(resp.usage, "prompt_tokens", None),
            "completion_tokens": getattr(resp.usage, "completion_tokens", None),
            "total_tokens": getattr(resp.usage, "total_tokens", None),
        }
    elif isinstance(resp, dict) and "usage" in resp:
        usage = resp.get("usage")

    return (answer or "").strip(), usage

def _get_delta_text(chunk: Any) -> Optional[str]:
    """
    兼容对象/字典：
    - chunk.choices[0].delta.content
    - chunk["choices"][0]["delta"]["content"]
    - 极少数 SDK 可能用 choices[0].message.content（尾包）
    """
    try:
        choices = getattr(chunk, "choices", None) or chunk.get("choices")
        if not choices:
            return None
        c0 = choices[0]
        delta = getattr(c0, "delta", None) if hasattr(c0, "delta") else c0.get("delta")
        if delta and (hasattr(delta, "content") or isinstance(delta, dict)):
            return getattr(delta, "content", None) if hasattr(delta, "content") else delta.get("content")
        # 末包可能直接给出 message.content
        message = getattr(c0, "message", None) if hasattr(c0, "message") else c0.get("message")
        if message:
            return getattr(message, "content", None) if hasattr(message, "content") else message.get("content")
    except Exception:
        return None
    return None

def _sse(data: Dict[str, Any]) -> str:
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

# ============ Middleware: per-request total timing ============
@app.middleware("http")
async def timing_middleware(request: Request, call_next):
    t0 = time.perf_counter()
    response = await call_next(request)
    total_ms = round((time.perf_counter() - t0) * 1000, 3)
    log.info(f"[TIMING] method={request.method} path={request.url.path} total={total_ms}ms")
    response.headers["X-Total-Time-ms"] = str(total_ms)
    return response

# ============ Routes ============
@app.get("/healthz")
def healthz():
    return {"ok": True, "model": MODEL_NAME, "time": _now_iso()}

# —— 单轮 RAG（保留原有接口） ——
@app.post("/rag", response_model=RagResponse)
def rag_endpoint(payload: RagRequest = Body(...)):
    timer = Timer()
    with timer.span("build_payload"):
        user_payload = _build_user_payload(payload.query, payload.retrieved_text)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_payload},
    ]

    with timer.span("llm_call"):
        try:
            resp = _call_zhipu(messages, MODEL_NAME, payload.temperature, payload.max_tokens)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"ZhipuAI 调用失败: {e}")

    with timer.span("extract_usage"):
        answer, usage = _extract_answer_and_usage(resp)

    total = timer.done()
    log.info(f"[RAG] total={total}ms | " + ", ".join(f"{k}={v}ms" for k, v in timer.spans.items()))

    meta = payload.meta or {}
    meta["timings"] = {"total_ms": total, **timer.spans}

    return RagResponse(
        answer=answer,
        model=MODEL_NAME,
        created=_now_iso(),
        usage=usage,
        meta=meta,
        session_id=None
    )

# ======== 新增：RAG 流式 ========
@app.post("/rag/stream")
def rag_stream_endpoint(payload: RagRequest = Body(...)):
    timer = Timer()

    def gen() -> Generator[str, None, None]:
        nonlocal timer
        try:
            with timer.span("build_payload"):
                user_payload = _build_user_payload(payload.query, payload.retrieved_text)

            messages = [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_payload},
            ]

            yield _sse({"event": "start", "model": MODEL_NAME, "created": _now_iso()})

            with timer.span("llm_stream"):
                stream = _call_zhipu_stream(messages, MODEL_NAME, payload.temperature, payload.max_tokens)

                for chunk in stream:
                    delta = _get_delta_text(chunk)
                    if delta:
                        yield _sse({"delta": delta})

            # 流式结束后做一次 usage 汇总（如 SDK 支持）
            with timer.span("finalize"):
                # 某些 SDK 提供 stream.get_final_response()；如无则跳过
                usage = None
                try:
                    final_resp = getattr(stream, "get_final_response", lambda: None)()
                    if final_resp:
                        _, usage = _extract_answer_and_usage(final_resp)
                except Exception:
                    usage = None

                total = timer.done()
                timings = {"total_ms": total, **timer.spans}
                yield _sse({"event": "done", "usage": usage, "timings": timings})
        except Exception as e:
            err = {"event": "error", "message": f"ZhipuAI 流式失败: {str(e)}"}
            yield _sse(err)

    return StreamingResponse(gen(), media_type="text/event-stream")

# —— 会话管理 ——
@app.post("/sessions", response_model=CreateSessionResponse, summary="创建新会话")
def create_session(req: CreateSessionRequest = Body(default=None)):
    sid = _init_session(req.system_prompt if req else None)
    return CreateSessionResponse(session_id=sid, created=sessions[sid]["created"])

@app.get("/sessions/{session_id}", response_model=SessionDump, summary="查看会话消息（含system）")
def get_session(session_id: str = Path(...)):
    sess = sessions.get(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="会话不存在")
    return SessionDump(
        session_id=session_id,
        created=sess["created"],
        updated=sess["updated"],
        messages=sess["messages"]
    )

@app.delete("/sessions/{session_id}", summary="删除会话")
def delete_session(session_id: str = Path(...)):
    with lock:
        if session_id in sessions:
            del sessions[session_id]
            return {"ok": True}
    raise HTTPException(status_code=404, detail="会话不存在")

@app.post("/sessions/{session_id}/reset", summary="清空会话历史但保留会话ID")
def reset_session(session_id: str = Path(...), req: CreateSessionRequest = Body(default=None)):
    with lock:
        if session_id not in sessions:
            raise HTTPException(status_code=404, detail="会话不存在")
        system_prompt = (req.system_prompt if req and req.system_prompt else sessions[session_id]["messages"][0]["content"])
        sessions[session_id] = {
            "created": sessions[session_id]["created"],
            "updated": _now_iso(),
            "messages": [{"role": "system", "content": system_prompt}],
        }
    return {"ok": True, "session_id": session_id}

# —— 多轮对话（保留原有同步版） ——
@app.post("/chat", response_model=ChatResponse, summary="多轮对话（可携带RAG召回）")
def chat(payload: ChatRequest = Body(...)):
    timer = Timer()

    # 1) 确保会话存在（可自动创建）
    with timer.span("ensure_session"):
        sid = payload.session_id or _init_session()

    # 2) 追加本轮 user（包含 RAG 召回）
    with timer.span("build_payload"):
        user_msg = _build_user_payload(payload.query, payload.retrieved_text)

    with timer.span("append_trim"):
        _append_and_trim(sid, "user", user_msg)

    # 3) 调用 LLM
    with timer.span("snapshot_messages"):
        with lock:
            messages = list(sessions[sid]["messages"])
            turn_index = sum(1 for m in messages if m["role"] == "assistant")

    try:
        with timer.span("llm_call"):
            resp = _call_zhipu(messages, MODEL_NAME, payload.temperature, payload.max_tokens)
    except Exception as e:
        with lock:
            sessions[sid]["messages"].pop()  # 回滚 user
        raise HTTPException(status_code=500, detail=f"ZhipuAI 调用失败: {e}")

    # 4) 取答案并写入历史
    with timer.span("extract_usage"):
        answer, usage = _extract_answer_and_usage(resp)

    with timer.span("append_assistant"):
        _append_and_trim(sid, "assistant", answer)

    total = timer.done()
    log.info(f"[CHAT] sid={sid} total={total}ms | " + ", ".join(f"{k}={v}ms" for k, v in timer.spans.items()))

    meta = payload.meta or {}
    meta["timings"] = {"total_ms": total, **timer.spans}

    return ChatResponse(
        session_id=sid,
        answer=answer,
        model=MODEL_NAME,
        created=_now_iso(),
        usage=usage,
        turn_index=turn_index + 1,
        meta=meta
    )

# ======== 新增：多轮对话流式 ========
@app.post("/chat/stream", summary="多轮对话流式（可携带RAG召回）")
def chat_stream(payload: ChatRequest = Body(...)):
    timer = Timer()

    def gen() -> Generator[str, None, None]:
        nonlocal timer
        sid_created_here = False
        assistant_acc = []  # 累积文本用于写回历史
        try:
            # 1) 会话
            with timer.span("ensure_session"):
                sid = payload.session_id
                if not sid:
                    sid = _init_session()
                    sid_created_here = True

            # 2) 追加本轮 user
            with timer.span("build_payload"):
                user_msg = _build_user_payload(payload.query, payload.retrieved_text)

            with timer.span("append_trim"):
                _append_and_trim(sid, "user", user_msg)

            with timer.span("snapshot_messages"):
                with lock:
                    messages = list(sessions[sid]["messages"])
                    turn_index = sum(1 for m in messages if m["role"] == "assistant") + 1

            yield _sse({"event": "start", "session_id": sid, "turn_index": turn_index, "model": MODEL_NAME, "created": _now_iso()})

            # 3) 流式
            with timer.span("llm_stream"):
                stream = _call_zhipu_stream(messages, MODEL_NAME, payload.temperature, payload.max_tokens)
                for chunk in stream:
                    delta = _get_delta_text(chunk)
                    if delta:
                        assistant_acc.append(delta)
                        yield _sse({"delta": delta})

            # 4) 写入历史 + usage/timings
            with timer.span("append_assistant"):
                final_text = "".join(assistant_acc)
                _append_and_trim(sid, "assistant", final_text)

            with timer.span("finalize"):
                usage = None
                try:
                    final_resp = getattr(stream, "get_final_response", lambda: None)()
                    if final_resp:
                        _, usage = _extract_answer_and_usage(final_resp)
                except Exception:
                    usage = None

                total = timer.done()
                timings = {"total_ms": total, **timer.spans}
                yield _sse({"event": "done", "session_id": sid, "turn_index": turn_index, "usage": usage, "timings": timings})

        except Exception as e:
            # 回滚 user（仅当本轮 user 已写入且 assistant 未成功）
            try:
                if assistant_acc == [] and not sid_created_here and payload.session_id:
                    with lock:
                        if payload.session_id in sessions and sessions[payload.session_id]["messages"]:
                            # 尾部应为本轮 user
                            sessions[payload.session_id]["messages"].pop()
            except Exception:
                pass
            yield _sse({"event": "error", "message": f"ZhipuAI 流式失败: {str(e)}"})

    return StreamingResponse(gen(), media_type="text/event-stream")

if __name__ == "__main__":
    # 注意：如果文件名是 app.py，应为 "app:app"
    uvicorn.run("app:app", host="0.0.0.0", port=APP_PORT, reload=False)
