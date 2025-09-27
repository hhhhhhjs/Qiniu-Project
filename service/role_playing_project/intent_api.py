# filename: intent_api.py
import os
import json
import re
from typing import Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI

# ====== 配置 ======
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")
MODEL_NAME = os.getenv("ZHIPUAI_MODEL", "glm-4.5")   # 或 "glm-4.5-flash"
TIMEOUT = float(os.getenv("ZHIPUAI_TIMEOUT", "30"))

if not ZHIPUAI_API_KEY:
    raise RuntimeError("请先设置环境变量 ZHIPUAI_API_KEY")

client = ZhipuAI(api_key=ZHIPUAI_API_KEY)
app = FastAPI(title="Roleplay Intent Detection API")
# === 全局启用 CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 前端的域名+端口
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ====== 输入/输出模型 ======
class IntentRequest(BaseModel):
    text: str = Field(..., description="用户原始输入")

class IntentResponse(BaseModel):
    is_roleplay: bool = Field(..., description="是否包含扮演角色意图")
    intent_label: str = Field(..., description="意图标签: roleplay / not_roleplay / unsure")
    confidence: float = Field(..., ge=0, le=1, description="置信度 0~1")
    role_name: Optional[str] = Field(None, description="抽取到的角色名/身份（可选）")
    triggers: Optional[list[str]] = Field(default=None, description="触发判断的关键词或句式")
    reasoning: Optional[str] = Field(default=None, description="简要判断依据")

# ====== 提示词（严格JSON） ======
SYSTEM_PROMPT = """你是一个NLP分类器，任务是判断用户是否在表达“扮演某个角色/人物/身份”的意图。
请**仅**输出合法的JSON，符合如下模式（不要有多余文本或注释）：
{
  "is_roleplay": <bool>,
  "intent_label": "<roleplay|not_roleplay|unsure>",
  "confidence": <0.0-1.0>,
  "role_name": "<string or null>",
  "triggers": ["<string>", "..."] or [],
  "reasoning": "<string>"
}
判定要点：
- 典型触发词：扮演/角色/假装/当作/模仿/以XX身份/Roleplay/RP/代入/你现在是...
- 也包含隐性表达，如“接下来你是我的律师”“请以老师身份回答”等。
- 如果是“写一个角色”“给我一个人物设定”，但不要求你扮演，只是生成设定 => not_roleplay。
- 无法确定时 intent_label = "unsure"，confidence <= 0.6。
- role_name 尽量抽取（如“李白”“律师”“猫娘”“面试官”），没有则为 null。
- 严格输出JSON，无解释文字。
"""

FEW_SHOTS = [
    {"role": "user", "content": "我们来玩角色扮演，你当我的英语老师，纠正我发音。"},
    {"role": "assistant", "content": json.dumps({
        "is_roleplay": True,
        "intent_label": "roleplay",
        "confidence": 0.95,
        "role_name": "英语老师",
        "triggers": ["角色扮演", "你当我的", "老师"],
        "reasoning": "明确提出角色扮演并指定老师身份"
    }, ensure_ascii=False)},
    {"role": "user", "content": "请给我一个‘中世纪骑士’的人物小传和设定，不需要你扮演。"},
    {"role": "assistant", "content": json.dumps({
        "is_roleplay": False,
        "intent_label": "not_roleplay",
        "confidence": 0.88,
        "role_name": None,
        "triggers": ["人物设定"],
        "reasoning": "仅请求生成设定，不要求助理代入角色"
    }, ensure_ascii=False)},
    {"role": "user", "content": "后面的问题请以资深面试官的视角来点评我的答案。"},
    {"role": "assistant", "content": json.dumps({
        "is_roleplay": True,
        "intent_label": "roleplay",
        "confidence": 0.9,
        "role_name": "资深面试官",
        "triggers": ["以…的视角", "面试官"],
        "reasoning": "要求助理以某角色身份作答"
    }, ensure_ascii=False)},
]

def _safe_json_loads(s: str) -> Dict[str, Any]:
    """尽可能稳健地从LLM响应中抽取JSON。"""
    # 1) 直接尝试
    try:
        return json.loads(s)
    except Exception:
        pass
    # 2) 正则提取首个花括号JSON块
    m = re.search(r"\{(?:[^{}]|(?R))*\}", s, flags=re.DOTALL)
    if m:
        try:
            return json.loads(m.group(0))
        except Exception:
            pass
    raise ValueError("LLM未返回合法JSON")

@app.post("/v1/intent/roleplay", response_model=IntentResponse)
def detect_roleplay_intent(req: IntentRequest):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + FEW_SHOTS + [
            {"role": "user", "content": req.text}
        ]

        resp = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1,
            max_tokens=300,
            top_p=0.9,
            timeout=TIMEOUT,
        )

        content = resp.choices[0].message.content if resp and resp.choices else ""
        data = _safe_json_loads(content)

        # pydantic校验 & 规范化
        parsed = IntentResponse(**data)
        return parsed

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ZhipuAI 调用或解析失败: {e}")
