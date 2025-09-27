import os
import json
from typing import Dict, Any, Generator
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
MODEL_NAME = os.getenv("ZHIPUAI_MODEL", "glm-4.5")  # 可改为 glm-4.5-flash 追求更快首 token

if not ZHIPUAI_API_KEY:
    raise RuntimeError("请先设置环境变量 ZHIPUAI_API_KEY")

client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

app = FastAPI(title="Roleplay Streaming API")

# —— 你的工作流 System Prompt（信息提取 + 自我介绍 + 严格 JSON）——
ROLEPLAY_SYSTEM_PROMPT = """你是一名角色扮演助手。  
用户可能会输入类似“扮演XXX”的请求。  
请你严格按照以下两步完成任务，并用 JSON 格式输出最终结果：

### 第一步：信息提取
1. 从用户输入中提取 **角色名字**。
2. 查询或推理该角色的 **职业/身份**。
3. 查询或推理该角色的 **能力/技能**。
4. 分析该角色常见的 **说话语气/风格**。

### 第二步：自我介绍生成
根据提取的角色信息，生成一段 **自我介绍**，要求符合该角色的职业、能力和说话语气风格。  
内容尽量自然，不要出现“我是一个虚拟角色”或“我是AI”之类的说明。  

### 输出格式（必须严格符合）
{
  "role_name": "...",
  "profession": "...",
  "abilities": ["...","..."],
  "style": "...",
  "self_introduction": "..."
}

请直接输出上述 JSON（不需要额外解释），确保是合法 JSON。"""

class RPRequest(BaseModel):
    text: str = Field(..., description="用户原始输入，如：扮演哈利波特 / 帮我扮演孙悟空")

def sse_pack(event: str, data: Any) -> str:
    """SSE 格式化（event + data），客户端更易区分不同阶段"""
    if not isinstance(data, str):
        data = json.dumps(data, ensure_ascii=False)
    return f"event: {event}\ndata: {data}\n\n"

def roleplay_stream(text: str) -> Generator[bytes, None, None]:
    """
    以 SSE 方式边生成边返回：
      - 先把“开始”事件发给前端，便于立刻渲染。
      - 中途逐 token 流式发送（event: delta）。
      - 结束时再发送一次“final”事件，附带完整 JSON。
    """
    # 预告开始（可用于前端立刻展示“加载中”）
    yield sse_pack("start", {"message": "streaming start"}).encode("utf-8")

    # 触发流式
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": ROLEPLAY_SYSTEM_PROMPT},
            {"role": "user", "content": text},
        ],
        temperature=0.2,          # 低温度=更稳定结构化
        top_p=0.95,
        stream=True               # !!! 开启流式
    )

    # 累积完整文本，流末尾再解析为 JSON，便于“最终结构化结果”
    full_text = []

    # 不同 SDK 版本的字段名可能微差，这里做了兼容判断
    for chunk in stream:
        try:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            # 新版：delta.content；旧版可能是 choices[0].delta.get("content")
            if isinstance(delta, dict):
                piece = delta.get("content") or ""
            else:
                piece = getattr(delta, "content", "") or ""

            if piece:
                full_text.append(piece)
                # 直接把片段以 delta 事件丢出去
                yield sse_pack("delta", piece).encode("utf-8")
        except Exception as e:
            # 流中容错：不中断输出
            yield sse_pack("warn", {"error": str(e)}).encode("utf-8")

    # 合并完整文本
    final_text = "".join(full_text).strip()

    # 保底：尝试把模型输出解析为 JSON；若失败则兜底成一个包装 JSON
    try:
        final_json = json.loads(final_text)
        # 校验关键字段，缺失时做保底处理
        final_json.setdefault("role_name", "")
        final_json.setdefault("profession", "")
        final_json.setdefault("abilities", [])
        final_json.setdefault("style", "")
        final_json.setdefault("self_introduction", "")
    except Exception:
        # 如果大模型没能严格闭合 JSON（少数情况下可能发生），做一次安全兜底
        final_json = {
            "role_name": "",
            "profession": "",
            "abilities": [],
            "style": "",
            "self_introduction": "",
            "_raw": final_text  # 保留原始文本，便于前端或服务侧观测
        }

    # 发送最终 JSON
    yield sse_pack("final", final_json).encode("utf-8")
    yield sse_pack("end", {"message": "streaming end"}).encode("utf-8")

@app.post("/v1/roleplay/stream")
def roleplay_endpoint(req: RPRequest):
    """
    SSE 流式接口：
    - Content-Type: text/event-stream
    - events:
        start  -> 流开始提示
        delta  -> 逐片段文本（模型边生成边发）
        final  -> 完整 JSON（严格结构化结果）
        end    -> 流结束提示
    """
    return StreamingResponse(
        roleplay_stream(req.text),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Nginx 场景下降低缓冲
        },
    )
