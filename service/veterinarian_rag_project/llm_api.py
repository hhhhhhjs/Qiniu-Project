#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from typing import Optional, Dict, Any, Generator

from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from zhipuai import ZhipuAI

# ========= 基础配置 =========
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
MODEL_NAME = os.getenv("ZHIPUAI_MODEL", "glm-4.5")  # 要求使用 glm-4.5

if not ZHIPUAI_API_KEY:
    raise RuntimeError("请先设置环境变量 ZHIPUAI_API_KEY")

client = ZhipuAI(api_key=ZHIPUAI_API_KEY)

app = FastAPI(title="Pet Roleplay Streaming API", version="1.0.0")

# CORS（开发期放开，生产建议收敛到具体域名）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # 生产建议改成你的前端域名
    allow_credentials=False,    # 前端如不带 cookie 建议 False
    allow_methods=["*"],
    allow_headers=["*"],
)

# ========= 角色 System Prompt =========
ROLE_SYSTEM_PROMPT = """你现在扮演一名猫狗识别与养护专家助理，姓名：小集（女性）。
口吻：专业、温柔、清晰、以行动建议为中心；避免夸张语气与不确定性陈述。
身份边界：不是临床兽医；在紧急或疑似重症时必须建议线下就医。

【你的任务】
- 结合“召回文本内容”与“用户问题”，给出准确、可执行的养护建议。
- 以“召回内容”为主要依据；当召回不足时，补充通用养护常识，但需要显式标注“基于通用常识”。
- 尽量用结构化输出，先结论后步骤，并给出可落地的操作要点与注意事项。

【可用输入（由上游传入）】
- 用户请求：{USER_QUERY} （文本；可为空）
- 召回内容：{RETRIEVED_TEXT}

【输出结构】
1. 一句话结论（先说能不能做/大方向）。
2. 分场景建议（按轻重缓急或时间线组织）：
   - 立刻：…
   - 24–48 小时内：…
   - 长期：…
3. 风险与红线：出现 A/B/C 立即就医。
4. 参考来源：［…］
5. （可选）需要的补充信息（仅当必要时 1 句）

【风格与格式】
- 用简明中文，短句＋要点清单。单位用“公制”（kg、mL、℃）。
- 避免药物剂量与诊疗方案的具体数值；如用户要求用药，统一提示“遵医嘱/线下兽医评估”。
- 不过度拟人化，不夸张；不得使用表情。
- 不编造来源；不确定就直说不确定，并给出获取确定性的最小化建议（如“提供体重/粪便照片”）。

【安全与合规】
- 紧急或高度可疑情况（大量出血、持续抽搐、高热不退、异物误食、无法站立/排尿、剧烈呼吸困难等）必须在结论段立即提醒就医。
- 不提供自制处方或禁药的用法；不指导侵入性操作。
- 严格按“【输出结构】”产出，先结论后步骤。
"""

# ========= 请求/响应模型 =========
class RoleplayRequest(BaseModel):
    user_query: Optional[str] = Field("", description="用户问题（支持为空）")
    retrieved_text: str = Field(..., description="召回文本内容（RAG召回结果）")

# ========= 工具：拼装 messages =========
def build_messages(user_query: str, retrieved_text: str) -> list[Dict[str, Any]]:
    # System 放角色与格式约束；User 放实际可用输入（用户问题 + 召回内容）
    system_msg = {"role": "system", "content": ROLE_SYSTEM_PROMPT}
    user_msg = {
        "role": "user",
        "content": (
            f"【输入】\n"
            f"用户请求：{user_query if user_query else '（空）'}\n"
            f"召回内容：\n{retrieved_text}\n\n"
            f"【请开始输出】严格遵循“【输出结构】”，避免给出药物剂量或诊疗方案具体数值。"
        )
    }
    return [system_msg, user_msg]

# ========= 核心：SSE 流式生成器 =========
def sse_stream(messages: list[Dict[str, Any]]) -> Generator[str, None, None]:
    """
    以 text/event-stream 流式输出增量内容。
    每个增量包裹为：data: {"delta":"..."}\n\n
    结束包：data: [DONE]\n\n
    """
    try:
        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.3,  # 稳健、少发散
            stream=True
        )

        for event in resp:
            # 兼容不同 SDK 的增量结构
            delta_text = None
            try:
                # 常见：choices[0].delta.content
                ch0 = event.choices[0] if getattr(event, "choices", None) else None
                if ch0 and getattr(ch0, "delta", None):
                    delta_text = ch0.delta.get("content")
                # 有些实现：choices[0].message.content（非流式或最后补齐）
                if (not delta_text) and ch0 and getattr(ch0, "message", None):
                    delta_text = ch0.message.get("content")
            except Exception:
                # 兜底：尝试 event 本身序列化后解析
                pass

            if delta_text:
                yield "data: " + json.dumps({"delta": delta_text}, ensure_ascii=False) + "\n\n"

        # 结束标识
        yield "data: [DONE]\n\n"

    except Exception as e:
        # 将异常以 error 事件抛给前端（也可直接抛 HTTP 502）
        err = {"error": f"{type(e).__name__}: {str(e)}"}
        yield "event: error\n"
        yield "data: " + json.dumps(err, ensure_ascii=False) + "\n\n"

# ========= 路由：流式输出 =========
@app.post("/v1/roleplay/stream")
def roleplay_stream(req: RoleplayRequest = Body(...)):
    messages = build_messages(req.user_query or "", req.retrieved_text)

    # 也可以在这里做召回文本截断或token预算控制（如有需要）
    # e.g., retrieved_text = req.retrieved_text[:4000]

    return StreamingResponse(
        sse_stream(messages),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )

# ========= 本地启动 =========
# uvicorn roleplay_stream_api:app --host 0.0.0.0 --port 9103 --workers 1
