import os
import json
from typing import List, Optional, Generator
from fastapi import FastAPI, Body
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI
from fastapi.middleware.cors import CORSMiddleware

ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
MODEL_NAME = os.getenv("ZHIPUAI_MODEL", "glm-4.5-flash")  # flash 首 token 更快

if not ZHIPUAI_API_KEY:
    raise RuntimeError("请先设置环境变量 ZHIPUAI_API_KEY")

client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

app = FastAPI(title="Role Chat Streaming API", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 前端的域名+端口
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# —— 角色扮演 System Prompt 模版 ——
ROLEPLAY_PROMPT_TEMPLATE = """从现在开始，你将完全扮演以下角色：{role_name}。
请严格遵循下面的设定：

- 职业/身份：{profession}
- 能力/技能：{abilities}
- 说话语气/风格：{style}

要求：
1. 你必须以 {role_name} 的第一人称来回答。
2. 不得提及“我是AI/模型/虚拟角色”等元信息。
3. 回答要符合该角色的背景、能力和语气风格。
4. 如果用户问到超出角色知识范围的问题，可以结合角色身份合理想象或回答，但不要跳出角色设定。

示例：
如果用户输入“你好”，而当前角色是“哈利波特”，你应该回答：
“你好，我是哈利波特，来自霍格沃茨魔法学校，很高兴认识你！”

现在，请开始扮演 {role_name}。"""

class RoleChatRequest(BaseModel):
    role_name: str = Field(..., description="角色名，例如：哈利波特 / 孙悟空")
    profession: str = Field(..., description="职业/身份")
    abilities: List[str] | str = Field(..., description="能力/技能，数组或以逗号分隔的字符串")
    style: str = Field(..., description="说话语气/风格")
    user_input: str = Field(..., description="用户这轮问题/消息")
    # 可选：对话历史（由你在业务侧维护，提升上下文一致性与连贯性）
    history: Optional[List[dict]] = Field(
        default=None,
        description='形如 [{"role":"user","content":"..."},{"role":"assistant","content":"..."}]'
    )

def _abilities_to_str(abilities: List[str] | str) -> str:
    if isinstance(abilities, list):
        return "、".join(abilities)
    return str(abilities)

def sse_pack(event: str, data: str) -> bytes:
    return f"event: {event}\ndata: {data}\n\n".encode("utf-8")

def role_chat_stream(payload: RoleChatRequest) -> Generator[bytes, None, None]:
    # 立即返回一个“开始”事件，降低感知时延
    yield sse_pack("start", '{"message":"streaming start"}')

    system_prompt = ROLEPLAY_PROMPT_TEMPLATE.format(
        role_name=payload.role_name,
        profession=payload.profession,
        abilities=_abilities_to_str(payload.abilities),
        style=payload.style
    )

    # 构造 messages：system 注入角色设定；可拼上历史；本轮 user_input 放末尾
    messages = [{"role": "system", "content": system_prompt}]
    if payload.history:
        # 只拼接有限轮数（如最近 6~8 条），降低上下文长度→更快首 token
        tail = payload.history[-8:]
        for m in tail:
            if m.get("role") in ("user", "assistant") and "content" in m:
                messages.append({"role": m["role"], "content": m["content"]})
    messages.append({"role": "user", "content": payload.user_input})

    # 触发流式生成
    stream = client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
        temperature=0.3,     # 略低温度：更稳定角色语气，且利于解码速度
        top_p=0.9,           # 稍收敛，减少“犹豫”
        max_tokens=512       # 可根据业务需要调整
    )

    # 连续逐片段吐出 delta
    # 兼容不同 SDK 返回结构
    for chunk in stream:
        try:
            choices = getattr(chunk, "choices", None)
            if not choices:
                continue
            delta = getattr(choices[0], "delta", None)
            if isinstance(delta, dict):
                piece = delta.get("content") or ""
            else:
                piece = getattr(delta, "content", "") or ""
            if piece:
                yield sse_pack("delta", json.dumps(piece, ensure_ascii=False))
        except Exception as e:
            # 容错不中断
            yield sse_pack("warn", json.dumps({"error": str(e)}, ensure_ascii=False))

    # 收尾事件
    yield sse_pack("end", '{"message":"streaming end"}')

@app.post("/v1/rolechat/stream")
def rolechat_endpoint(body: RoleChatRequest = Body(...)):
    """
    SSE 流式角色对话：
      - 请求体：role_name, profession, abilities(数组或字符串), style, user_input, (可选)history
      - 事件流：
          start -> 立刻返回，提示开始
          delta -> 模型生成的文本增量（字符串片段）
          end   -> 结束
    """
    return StreamingResponse(
        role_chat_stream(body),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no"  # Nginx 下避免缓冲
        }
    )
