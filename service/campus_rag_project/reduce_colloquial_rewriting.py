import os
import time
import re
from typing import Any, Dict, List, Optional, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()
ZHIPU_API_KEY = os.getenv("ZHIPUAI_API_KEY")
if not ZHIPU_API_KEY:
    raise RuntimeError("Missing ZHIPUAI_API_KEY in environment")

client = ZhipuAI(api_key=ZHIPU_API_KEY)
app = FastAPI(title="Speech De-oralization API", version="1.0.0")

# --------- Schemas ---------
Language = Literal["auto", "zh", "en"]
Style = Literal["neutral", "formal", "concise"]
Punct = Literal["auto", "keep", "fix"]

class NormalizeRequest(BaseModel):
    text: str = Field(..., min_length=1, description="ASR 原始文本")
    language: Language = "auto"
    style: Style = "neutral"
    punctuation: Punct = "auto"
    remove_disfluencies: bool = True
    merge_repetitions: bool = True
    keep_fillers: bool = False
    preserve_entities: List[str] = Field(default_factory=lambda: ["PERSON","ORG","DATE","TIME","CARDINAL"])
    custom_glossary: Dict[str, str] = Field(default_factory=dict)
    redact_pii: bool = False
    max_tokens: int = 512
    return_diff: bool = True
    trace: bool = False

class ChangeItem(BaseModel):
    type: Literal["delete","replace","insert"]
    source: str
    target: str
    reason: str

class NormalizeResponse(BaseModel):
    cleaned_text: str
    changes: Optional[List[ChangeItem]] = None
    usage: Dict[str, Any]
    model: str = "glm-4.5-flash"
    warnings: List[str] = Field(default_factory=list)
    trace: Optional[Dict[str, Any]] = None


# --------- Prompt Builders ---------
SYSTEM_PROMPT = """你是一个“口语转书面”的文本编辑器。
目标：在不改变事实的前提下，将口语化 ASR 文本整理为流畅、简洁、规范的书面语。
通用规则：
1) 删除口头语、语气词、赘词（如：呃、嗯、就是、那个、然后、你知道吧）。
2) 合并重复与回环，消除病句，修复语法。
3) 根据需求补齐或修正标点与大小写；不要乱加感叹或语气。
4) 保留事实性信息与数值（日期、金额、比例、时间点），避免臆测或改写数字。
5) 对专有名词使用用户词典 custom_glossary，遇到冲突以词典为准。
6) 对 preserve_entities 中的实体，不改写其文本内容，仅在需要时做格式化（如空格）。
7) 若 redact_pii 为真，对电话/邮箱/身份证号做部分脱敏（例：138****5678）。
8) 输出仅为整理后的最终文本，不要解释过程，不要附加总结。
9) 若输入语句碎片化，允许适度重排，使语义连贯，但不得引入新信息。
语言策略：
- language=auto 时：检测输入主语言，按该语言输出；混合语以主语言为准。
风格：
- style=neutral：中性、清晰、完整。
- style=formal：更正式，适度书面化。
- style=concise：更短更紧凑，但保留关键信息。"""

def build_user_prompt(req: NormalizeRequest) -> str:
    header = (
        f"<language>: {req.language}\n"
        f"<style>: {req.style}\n"
        f"<punctuation>: {req.punctuation}\n"
        f"<remove_disfluencies>: {req.remove_disfluencies}\n"
        f"<merge_repetitions>: {req.merge_repetitions}\n"
        f"<keep_fillers>: {req.keep_fillers}\n"
        f"<preserve_entities>: {','.join(req.preserve_entities)}\n"
        f"<redact_pii>: {req.redact_pii}\n"
        f"<custom_glossary>: {req.custom_glossary}\n\n"
        "请将下面 ASR 文本去口语化，仅输出整理后的文本：\n"
    )
    return header + req.text


# --------- Utility (simple diff) ---------
def heuristic_changes(src: str, dst: str) -> List[ChangeItem]:
    """极简启发式：找出删掉的口头语 & 替换的重复，非严格对齐。"""
    changes: List[ChangeItem] = []

    fillers = ["呃","额","嗯","啊","就是","那个","然后","你知道吧","我觉得","怎么说呢"]
    for f in fillers:
        if f in src and f not in dst:
            changes.append(ChangeItem(type="delete", source=f, target="", reason="口语词清理"))

    # 标点修正提示（极简判断）
    def count_punc(s: str) -> int:
        return len(re.findall(r"[，。！？,.!?；;：:]", s))
    if abs(count_punc(dst) - count_punc(src)) >= 2:
        changes.append(ChangeItem(type="replace", source="标点", target="规范化标点", reason="标点修正/补齐"))

    # 重复合并检测（非常粗糙）
    repeats = re.findall(r"(\b[\u4e00-\u9fa5\w]{2,}\b)(?:\s*\1){1,}", src)
    for r in set(repeats):
        if r in src and r in dst and src.count(r) > dst.count(r):
            changes.append(ChangeItem(type="replace", source=f"{r}…重复", target=r, reason="重复合并"))

    return changes


# --------- Core Endpoint ---------
@app.post("/v1/normalize_speech", response_model=NormalizeResponse)
def normalize(req: NormalizeRequest):
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="text 不能为空")

    start = time.time()

    try:
        resp = client.chat.completions.create(
            model="glm-4.5-flash",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": build_user_prompt(req)}
            ],
            temperature=0.2,
            top_p=0.9,
            max_tokens=req.max_tokens,
        )
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 调用失败: {e}")

    # 兼容 SDK 返回结构（以下写法与官方常见结构一致）
    try:
        choice = resp.choices[0]
        cleaned = choice.message.content.strip()
        prompt_tokens = getattr(resp.usage, "prompt_tokens", None) or 0
        completion_tokens = getattr(resp.usage, "completion_tokens", None) or 0
        total_tokens = getattr(resp.usage, "total_tokens", None) or (prompt_tokens + completion_tokens)
    except Exception:
        raise HTTPException(status_code=500, detail="解析 LLM 响应失败")

    latency_ms = int((time.time() - start) * 1000)
    warnings: List[str] = []

    # 简单的安全/策略提醒
    if len(cleaned) == 0:
        warnings.append("清洗后文本为空，可能输入为纯口语词或噪声。")

    changes = heuristic_changes(req.text, cleaned) if req.return_diff else None

    trace = None
    if req.trace:
        trace = {
            "system_prompt_preview": SYSTEM_PROMPT[:200],
            "rules_applied": [
                *(["remove_disfluencies"] if req.remove_disfluencies else []),
                *(["merge_repetitions"] if req.merge_repetitions else []),
                *(["fix_punctuation"] if req.punctuation in ("auto", "fix") else []),
                *(["keep_fillers"] if req.keep_fillers else []),
            ],
        }

    return NormalizeResponse(
        cleaned_text=cleaned,
        changes=changes,
        usage={
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens,
            "latency_ms": latency_ms
        },
        model="glm-4.5-flash",
        warnings=warnings,
        trace=trace
    )
