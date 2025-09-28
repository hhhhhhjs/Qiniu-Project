# intent_api.py
import os
import json
from typing import Optional, Literal, Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from zhipuai import ZhipuAI  # pip install zhipuai

MODEL_NAME = os.getenv("GLM_MODEL", "glm-4.5")
ZHIPUAI_API_KEY = os.getenv("ZHIPUAI_API_KEY", "")

app = FastAPI(title="Pet Intent API", version="1.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_methods=["*"], allow_headers=["*"], allow_credentials=False,
)

class IntentRequest(BaseModel):
    query: str = Field(..., description="用户的自然语言问题")
    has_image: bool = Field(False, description="是否同时上传了图片（影响路由）")
    lang_hint: Optional[str] = Field(None, description="可选语言提示，如 zh/en")

class IntentResponse(BaseModel):
    want_image: bool
    animal: Literal["cat", "dog", "both", "unknown"]
    breed: Optional[str] = None
    intent: Literal["image_request", "care_request", "info_request", "other"]
    action: Literal["by-text", "by-image", "care"]  # 只有三种
    confidence: float = Field(ge=0.0, le=1.0)
    reason: str

def get_client() -> ZhipuAI:
    if not ZHIPUAI_API_KEY:
        raise RuntimeError("ZHIPUAI_API_KEY 未设置")
    return ZhipuAI(api_key=ZHIPUAI_API_KEY)

SYSTEM_PROMPT = (
    "你是一个意图分类器，专注判断用户是否在索要“猫/狗”的图片，并抽取动物与品种。\n"
    "只输出严格 JSON，不要任何额外文本、注释或反引号。\n"
    "字段：\n"
    " - want_image: boolean\n"
    " - animal: 'cat'|'dog'|'both'|'unknown'\n"
    " - breed: string|null\n"
    " - intent: 'image_request'|'care_request'|'info_request'|'other'\n"
    " - action: 'by-text'|'by-image'|'care'   # 只允许这三种\n"
    " - confidence: number(0..1)\n"
    " - reason: string\n"
    "\n"
    "判定要点：\n"
    "1) 用户明确要看猫/狗“图片/照片/图像/图”（photo/picture/image等）⇒ want_image=true。\n"
    "2) 与养护相关（喂养/梳理/疫苗/疾病/护理等）⇒ intent=care_request。\n"
    "3) 只询问信息（不是养护）如“英短是什么/性格如何”⇒ intent=info_request（但路由仍按下述规则）。\n"
    "4) 动物归类：含'猫/cat'⇒cat；含'狗/dog'⇒dog；两者都有⇒both；否则 unknown。\n"
    "5) 品种抽取：返回原样字符串（可中英文），没有则 null。\n"
    "6) 路由规则（非常重要）：\n"
    "   - 若 want_image=true 且 has_image=true  ⇒ action='by-image'（图搜文）\n"
    "   - 若 want_image=true 且 has_image=false ⇒ action='by-text'（文搜图）\n"
    "   - 其余所有情况（包括 info/other/care）一律 ⇒ action='care'\n"
    "7) 始终输出 JSON，严格字段名与取值。\n"
)

def call_glm(query: str, has_image: bool, lang_hint: Optional[str]) -> Dict[str, Any]:
    client = get_client()
    user_payload = {"query": query, "has_image": has_image, "lang_hint": lang_hint or ""}
    resp = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0.1,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": json.dumps(user_payload, ensure_ascii=False)},
        ],
    )
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
    except Exception:
        content = content.strip().strip("`")
        if content.lower().startswith("json"):
            content = content[4:].strip()
        data = json.loads(content)
    return {"parsed": data}

# —— 统一路由决策（强制覆盖）——
def decide_action(want_image: bool, has_image: bool) -> str:
    if want_image:
        return "by-image" if has_image else "by-text"
    return "care"

# —— LLM 失败的启发式回退 —— 
def heuristic_fallback(query: str, has_image: bool) -> Dict[str, Any]:
    q = query.lower()
    img_kw = any(k in q for k in ["图片", "照片", "图像", "来一张", "看看", "pic", "photo", "image", "picture", "show me"])
    is_cat = any(k in q for k in ["猫", "猫咪", "cat", "kitten"])
    is_dog = any(k in q for k in ["狗", "犬", "dog", "puppy"])
    animal = "both" if (is_cat and is_dog) else ("cat" if is_cat else ("dog" if is_dog else "unknown"))
    want_image = bool(img_kw)
    action = decide_action(want_image, has_image)
    intent = "image_request" if want_image else "care_request"  # 其余归 care
    return {
        "want_image": want_image,
        "animal": animal,
        "breed": None,
        "intent": intent,
        "action": action,
        "confidence": 0.55 if want_image else 0.5,
        "reason": "启发式回退：关键词与是否有图决定路由（其余一律care）",
    }

@app.post("/v1/intent", response_model=IntentResponse)
def detect_intent(req: IntentRequest):
    try:
        out = call_glm(req.query, req.has_image, req.lang_hint)
        data = out["parsed"]

        want_image = bool(data.get("want_image", False))
        # 统一覆盖 action：仅 by-text/by-image/care
        action = decide_action(want_image, req.has_image)

        resp = IntentResponse(
            want_image=want_image,
            animal=str(data.get("animal", "unknown")),
            breed=(data.get("breed") or None),
            intent=str(data.get("intent", "other")),
            action=action,
            confidence=float(data.get("confidence", 0.6 if want_image else 0.7)),
            reason=str(data.get("reason", ""))[:500] or "按统一规则覆盖路由（非图片诉求一律care）",
        )
        return resp

    except Exception:
        fb = heuristic_fallback(req.query, req.has_image)
        return IntentResponse(**fb)

@app.get("/healthz")
def healthz():
    return {"ok": bool(ZHIPUAI_API_KEY), "model": MODEL_NAME, "actions": ["by-text", "by-image", "care"]}
