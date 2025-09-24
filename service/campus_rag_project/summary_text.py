#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# 批量摘要：遍历 txt_data 下所有 .txt，输出到 summary_data，跳过脏数据并记录日志
# pip install -U zhipuai

import os
import re
import json
import traceback
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
from typing import List, Dict, Tuple

from zhipuai import ZhipuAI

# ===== 路径配置 =====
IN_DIR  = Path("/home/wmy/workspace/server/campus_rag_project/data/txt_data")
OUT_DIR = Path("/home/wmy/workspace/server/campus_rag_project/data/summary_data")
LOG_DIR = OUT_DIR / "_logs"
OUT_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# ===== 模型与参数 =====
MODEL = "glm-4.5-flash"
MAX_TOKENS = 1024
CHUNK_CHARS = 6000
OVERLAP = 200
USE_THINKING = True  # 若报参数错误，可改为 False

# ===== 质量门控阈值（可按需调整）=====
MIN_CHARS = 200
MIN_CN_CHARS = 50
MIN_SENTENCES = 3
MIN_UNIQUE_RATIO = 0.15
TITLE_ONLY_MAX_LINES = 5
TITLE_LIKE_PATTERNS = [
    r"(?i)\bFRESHMAN\s+HANDBOOK\b",
    r"新生手册",
    r"入学指南",
    r"报到须知",
    r"集美大学.*(新生|迎新)",
    r"^目[录次]?\s*$",
]

# ===== API Key =====
API_KEY = "4dc3c4e045814b799df1e7098228cf86.BeIMESXJ5LkjAnGf"
if not API_KEY:
    raise RuntimeError("请先 `export ZHIPUAI_API_KEY='你的Key'`。")

client = ZhipuAI(api_key=API_KEY)

@dataclass
class QualityReport:
    ok: bool
    reasons: List[str]
    metrics: Dict[str, float]

def read_text(path: Path) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()

def count_sentences(s: str) -> int:
    return len(re.findall(r"[。！？!?…]+|(?<!\d)\.(?!\d)", s))

def chinese_char_count(s: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", s))

def unique_token_ratio(s: str) -> float:
    tokens = re.findall(r"\S+", s)
    return (len(set(tokens)) / max(1, len(tokens))) if tokens else 0.0

def looks_like_title_only(s: str) -> Tuple[bool, str]:
    lines = [ln.strip() for ln in s.splitlines() if ln.strip()]
    if len(lines) <= TITLE_ONLY_MAX_LINES:
        joined = "\n".join(lines)
        for pat in TITLE_LIKE_PATTERNS:
            if re.search(pat, joined):
                return True, f"匹配到标题样式：{pat}"
    return False, ""

def assess_text_quality(s: str) -> QualityReport:
    length = len(s)
    cn = chinese_char_count(s)
    sentences = count_sentences(s)
    ur = unique_token_ratio(s)
    lines = len([ln for ln in s.splitlines() if ln.strip()])

    reasons = []
    is_title_only, why = looks_like_title_only(s)
    if is_title_only:
        reasons.append(why)
    if length < MIN_CHARS:
        reasons.append(f"文本过短 length={length} < {MIN_CHARS}")
    if cn < MIN_CN_CHARS:
        reasons.append(f"中文字符过少 cn={cn} < {MIN_CN_CHARS}")
    if sentences < MIN_SENTENCES:
        reasons.append(f"句子过少 sentences={sentences} < {MIN_SENTENCES}")
    if ur < MIN_UNIQUE_RATIO:
        reasons.append(f"信息密度低 unique_ratio={ur:.3f} < {MIN_UNIQUE_RATIO}")

    metrics = dict(
        length=length, chinese_chars=cn, sentences=sentences,
        unique_ratio=ur, nonempty_lines=lines,
    )
    ok = len(reasons) == 0
    return QualityReport(ok=ok, reasons=reasons, metrics=metrics)

def log_jsonl(entry: Dict):
    with open(LOG_DIR / "summary_log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def split_text(text: str, chunk_chars: int = CHUNK_CHARS, overlap: int = OVERLAP) -> List[str]:
    if len(text) <= chunk_chars:
        return [text]
    paras = text.split("\n\n")
    chunks, buf = [], ""
    for p in paras:
        p2 = (p + "\n\n")
        if len(buf) + len(p2) <= chunk_chars:
            buf += p2
        else:
            if buf:
                chunks.append(buf.strip())
            s = p2
            while len(s) > chunk_chars:
                head = s[:chunk_chars]
                chunks.append(head)
                s = s[chunk_chars - overlap:]
            buf = s
    if buf.strip():
        chunks.append(buf.strip())
    return chunks

def _extract_content(choice) -> str:
    msg = choice.message
    if isinstance(msg, dict):
        return msg.get("content", "")
    return getattr(msg, "content", "") or str(msg)

def call_summary(prompt: str, temperature: float = 0.3) -> str:
    kwargs = dict(
        model=MODEL,
        messages=[
            {"role": "system", "content": "你是资深中文摘要助手，输出结构化、精炼、客观。"},
            {"role": "user", "content": prompt},
        ],
        max_tokens=MAX_TOKENS,
        temperature=temperature,
    )
    if USE_THINKING:
        kwargs["thinking"] = {"type": "enabled"}
    try:
        resp = client.chat.completions.create(**kwargs)
    except Exception as e:
        # 如果 thinking 不被支持，自动降级重试
        if USE_THINKING:
            kwargs.pop("thinking", None)
            resp = client.chat.completions.create(**kwargs)
        else:
            raise e
    return _extract_content(resp.choices[0]).strip()

def summarize_long_text(text: str) -> str:
    chunks = split_text(text)
    if len(chunks) == 1:
        return call_summary(
            "请对以下文本进行中文摘要，给出：\n"
            "1) 200-300字的总摘要；\n2) 5-8条要点列表。\n\n文本：\n```text\n"
            + chunks[0] + "\n```"
        )
    part_summaries = []
    for i, c in enumerate(chunks, 1):
        part_summaries.append(
            call_summary(
                f"这是第 {i}/{len(chunks)} 个分块。请写一个80-150字的分块摘要，并给出3-5条关键要点：\n```text\n{c}\n```",
                temperature=0.2,
            )
        )
    merged = "\n\n".join([f"【分块{i}】\n{s}" for i, s in enumerate(part_summaries, 1)])
    return call_summary(
        "根据以下分块摘要，生成一个**整体中文摘要**：\n"
        "A. 先给出一段200-300字的总述；\n"
        "B. 再给出5-8条结构化要点（含事实、结论、数据/证据，如有）。\n\n"
        + merged,
        temperature=0.3,
    )

def process_file(src_path: Path) -> Dict:
    rel = src_path.relative_to(IN_DIR)                 # 相对路径
    out_file = OUT_DIR / rel.with_suffix("")           # 去掉 .txt
    out_file = out_file.with_name(out_file.name + "_summary.txt")
    out_file.parent.mkdir(parents=True, exist_ok=True)

    entry = {
        "ts": datetime.now().isoformat(timespec="seconds"),
        "file_in": str(src_path),
        "file_out": str(out_file),
        "status": "",
        "reasons": [],
        "metrics": {},
        "error": "",
    }

    try:
        text = read_text(src_path)
        report = assess_text_quality(text)
        entry["metrics"] = report.metrics

        if not report.ok:
            entry["status"] = "skipped"
            entry["reasons"] = report.reasons
            log_jsonl(entry)
            return entry

        summary = summarize_long_text(text)
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(summary)
        entry["status"] = "summarized"
        log_jsonl(entry)
        return entry

    except Exception as e:
        entry["status"] = "error"
        entry["error"] = f"{type(e).__name__}: {e}"
        entry["traceback"] = traceback.format_exc()
        log_jsonl(entry)
        return entry

def main():
    txt_files = sorted(IN_DIR.rglob("*.txt"))  # 递归遍历
    total = len(txt_files)
    summarized = skipped = errors = 0

    print(f"发现 {total} 个 .txt 文件，开始处理...\n")
    for i, p in enumerate(txt_files, 1):
        r = process_file(p)
        tag = r["status"]
        if tag == "summarized":
            summarized += 1
        elif tag == "skipped":
            skipped += 1
        else:
            errors += 1
        print(f"[{i:>4}/{total}] {tag.upper():10s}  -> {p}")

    print("\n====== 汇总 ======")
    print(f"总数: {total}")
    print(f"摘要: {summarized}")
    print(f"跳过: {skipped}")
    print(f"错误: {errors}")
    print(f"日志: {LOG_DIR / 'summary_log.jsonl'}")
    print(f"输出目录: {OUT_DIR}")

if __name__ == "__main__":
    main()
