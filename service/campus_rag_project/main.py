from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import requests
import time
import json
from datetime import datetime

app = FastAPI()

# ==== 可调参数 ====
REQ_TIMEOUT = 30.0  # 每个下游请求的超时（秒）

# 下游服务地址（必要时可改成环境变量）
URL_NORMALIZE = "http://localhost:9000/v1/normalize_speech"
URL_RECALL    = "http://localhost:9001/v1/recall"
URL_RERANK    = "http://localhost:9002/rerank"
URL_RAG       = "http://localhost:9003/rag/stream"   # <- LLM 流式 SSE

class QuestionRequest(BaseModel):
    text: str

class AnswerResponse(BaseModel):
    answer: str
    timings: dict
    total_ms: int

def _now():
    return datetime.utcnow().isoformat() + "Z"

def _dur_ms(t0):
    return int((time.perf_counter() - t0) * 1000)

# ===== SSE 工具 =====
def _sse(data: dict) -> str:
    # 统一 SSE 打包：data: {json}\n\n
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

def _iter_sse_lines(resp):
    """逐行读取 text/event-stream，只返回 data: ... 的 JSON 负载字符串。"""
    for raw in resp.iter_lines(decode_unicode=True):
        if not raw:
            continue
        if raw.startswith("data:"):
            yield raw[5:].strip()

# ===== 新增：流式工作流（边算边推） =====
@app.post("/v1/workflow/stream")
def workflow_stream(req: QuestionRequest):
    """
    流式工作流：
    1) normalize.done -> 2) recall.done -> 3) rerank.done -> 4) answer.delta* -> done
    事件格式（data字段内）：
      {"event":"start"|"normalize"|"recall"|"rerank"|"delta"|"done"|"error", ...}
    """
    def gen():
        t_all = time.perf_counter()
        timings = {}
        answer_acc = []

        # start
        yield _sse({"event": "start", "ts": _now()})

        # ---------------- 1) 去口语化 ----------------
        t0 = time.perf_counter()
        t_start = _now()
        original_text = req.text
        try:
            norm_resp = requests.post(
                URL_NORMALIZE,
                json={"text": original_text},
                timeout=REQ_TIMEOUT
            )
        except Exception as e:
            yield _sse({"event": "error", "stage": "normalize", "message": f"请求异常: {e}"})
            return
        if not norm_resp.ok:
            yield _sse({"event": "error", "stage": "normalize", "message": f"http {norm_resp.status_code}"})
            return
        try:
            normalized = norm_resp.json()["cleaned_text"]
        except Exception:
            yield _sse({"event": "error", "stage": "normalize", "message": "返回解析失败（缺少 cleaned_text）"})
            return

        timings["normalize"] = {
            "start": t_start,
            "end": _now(),
            "elapsed_ms": _dur_ms(t0)
        }
        yield _sse({
            "event": "normalize",
            "elapsed_ms": timings["normalize"]["elapsed_ms"],
            "text": normalized
        })

        # ---------------- 2) 文本召回 ----------------
        t0 = time.perf_counter()
        t_start = _now()
        try:
            recall_resp = requests.post(
                URL_RECALL,
                json={"queries": [{"text": normalized}]},
                timeout=REQ_TIMEOUT
            )
        except Exception as e:
            yield _sse({"event": "error", "stage": "recall", "message": f"请求异常: {e}"})
            return
        if not recall_resp.ok:
            yield _sse({"event": "error", "stage": "recall", "message": f"http {recall_resp.status_code}"})
            return
        try:
            recall_json = recall_resp.json()
            results = recall_json["results"]
            hits = results[0]["hits"] if results else []
        except Exception:
            yield _sse({"event": "error", "stage": "recall", "message": "返回解析失败（缺少 results/hits）"})
            return

        documents = [hit.get("entity", {}).get("_content", "") for hit in hits if hit.get("entity")]
        timings["recall"] = {
            "start": t_start,
            "end": _now(),
            "elapsed_ms": _dur_ms(t0),
            "hit_count": len(documents)
        }
        yield _sse({
            "event": "recall",
            "elapsed_ms": timings["recall"]["elapsed_ms"],
            "hit_count": len(documents)
        })

        # ---------------- 3) 重排序 ----------------
        best_doc = ""
        if documents:
            t0 = time.perf_counter()
            t_start = _now()
            try:
                rerank_resp = requests.post(
                    URL_RERANK,
                    json={"query": normalized, "documents": documents},
                    timeout=REQ_TIMEOUT
                )
            except Exception as e:
                yield _sse({"event": "error", "stage": "rerank", "message": f"请求异常: {e}"})
                return
            if not rerank_resp.ok:
                yield _sse({"event": "error", "stage": "rerank", "message": f"http {rerank_resp.status_code}"})
                return
            try:
                rerank_json = rerank_resp.json()
                rerank_results = rerank_json["results"]
                best_doc = (rerank_results[0]["document"] if rerank_results else "")
            except Exception:
                yield _sse({"event": "error", "stage": "rerank", "message": "返回解析失败（缺少 results/document）"})
                return

            timings["rerank"] = {
                "start": t_start,
                "end": _now(),
                "elapsed_ms": _dur_ms(t0),
                "candidates": len(documents)
            }
        else:
            timings["rerank"] = {
                "skipped": True,
                "reason": "no recall documents"
            }

        # 发送重排完成事件（简要回显选中文本前 120 字，避免过长）
        # preview = (best_doc[:120] + "…") if best_doc and len(best_doc) > 120 else best_doc
        preview = (best_doc) if best_doc and len(best_doc) > 120 else best_doc
        yield _sse({
            "event": "rerank",
            "elapsed_ms": timings["rerank"].get("elapsed_ms", 0),
            "skipped": timings["rerank"].get("skipped", False),
            "candidates": timings["rerank"].get("candidates", 0),
            "preview": preview
        })

        # ---------------- 4) RAG 生成（转发下游 SSE） ----------------
        t0 = time.perf_counter()
        t_start = _now()
        headers = {"Accept": "text/event-stream", "Content-Type": "application/json"}
        try:
            with requests.post(
                URL_RAG,
                json={"query": normalized, "retrieved_text": best_doc},
                headers=headers,
                stream=True,
                timeout=(5.0, None)  # 连接 5s，读取不超时
            ) as resp:
                if not resp.ok:
                    yield _sse({"event": "error", "stage": "rag", "message": f"http {resp.status_code}"})
                    return

                for line in _iter_sse_lines(resp):
                    if line == "[DONE]":
                        break
                    try:
                        obj = json.loads(line)
                    except Exception:
                        # 非 JSON 行忽略
                        continue

                    if obj.get("event") == "error":
                        yield _sse({"event": "error", "stage": "rag", "message": obj.get("message", "unknown error")})
                        return

                    # 转发增量
                    delta = obj.get("delta")
                    if isinstance(delta, str) and delta:
                        answer_acc.append(delta)
                        yield _sse({"event": "delta", "text": delta})

                    # 若下游给了 done：提前拿到 usage/timings
                    if obj.get("event") == "done":
                        timings["rag_stream_timings"] = obj.get("timings")
                        rag_usage = obj.get("usage")
                        if rag_usage:
                            timings["rag_usage"] = rag_usage
                        break

        except Exception as e:
            yield _sse({"event": "error", "stage": "rag", "message": f"请求异常: {e}"})
            return

        # rag 阶段本地耗时记录
        timings["rag"] = {
            "start": t_start,
            "end": _now(),
            "elapsed_ms": _dur_ms(t0),
            "retrieved_used": bool(best_doc)
        }

        # 总结并结束
        total_ms = _dur_ms(t_all)
        final_answer = "".join(answer_acc).strip()
        # 服务端日志（可选）
        print(
            f"[WORKFLOW-STREAM] total={total_ms}ms | "
            f"normalize={timings.get('normalize',{}).get('elapsed_ms','-')}ms, "
            f"recall={timings.get('recall',{}).get('elapsed_ms','-')}ms, "
            f"rerank={timings.get('rerank',{}).get('elapsed_ms','-')}ms, "
            f"rag={timings.get('rag',{}).get('elapsed_ms','-')}ms | "
            f"hits={timings.get('recall',{}).get('hit_count','0')} "
            f"retrieved_used={timings.get('rag',{}).get('retrieved_used', False)}"
        )

        yield _sse({
            "event": "done",
            "answer": final_answer,    # 客户端也能一次性拿到完整答案（可选）
            "timings": timings,
            "total_ms": total_ms,
            "ts": _now()
        })

    return StreamingResponse(gen(), media_type="text/event-stream")
