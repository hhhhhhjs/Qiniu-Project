# ingest_care_txt_lite_safe.py
# 更稳健的入库流程：延迟建索引、限长、重试、断点续传、限速
import os, re, sys, time, json, hashlib, signal
from pathlib import Path
from typing import List, Dict, Tuple, Optional

import requests
from pymilvus import MilvusClient, DataType

# ================= 配置 =================
TXT_DIR   = Path("/home/wmy/workspace/server/veterinarian_rag_project/data/pet/ocr_txt")
DB_URI    = "./petkb.db"              # Milvus Lite 文件
COLL_NAME = "pet_knowledge_base"
DIM       = 1024
EMBED_API = "http://127.0.0.1:9200/v1/embed/text"  # 你的向量服务
INSERT_BATCH = int(os.getenv("INSERT_BATCH", "32"))  # 更小更稳
SLEEP_BETWEEN_BATCH = float(os.getenv("SLEEP_BETWEEN_BATCH", "0.05"))
EMBED_TIMEOUT = 60
EMBED_MAX_CHARS = int(os.getenv("EMBED_MAX_CHARS", "512"))  # 保守截断
EMBED_MAX_RETRY = 4
STATE_PATH = Path(".ingest_state.json")

# chunking 规则（适度收紧，降低长度分布尾部风险）
CHUNK_MIN = 150
CHUNK_MAX = 300
SENT_OVERLAP = 1

# ================ 工具 ================
PAGE_DIV_RE = re.compile(r"^=+\s*PAGE\s*\d{1,5}\s*=+$")
SENT_SPLIT_RE = re.compile(r"(?<=[。！？!?；;])\s+")
SOFT_JOIN_RE = re.compile(r"[。！？!?；;:：…]$")

def guess_species(slug: str) -> Dict[str, str]:
    return {"species_id": slug.replace(" ", "_"), "species_name": slug}

def read_txt(path: Path) -> str:
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read()
        except Exception:
            continue
    return path.read_text("utf-8", errors="ignore")

def clean_text(raw: str) -> str:
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [ln.strip() for ln in text.split("\n")]
    lines = [ln for ln in lines if not PAGE_DIV_RE.match(ln)]
    merged, buf = [], ""
    for ln in lines:
        if not ln:
            if buf:
                merged.append(buf)
                buf = ""
            merged.append("")
            continue
        if not buf:
            buf = ln
        else:
            if SOFT_JOIN_RE.search(buf):
                merged.append(buf); buf = ln
            else:
                buf = (buf + " " + ln).strip()
    if buf: merged.append(buf)
    out, prev_empty = [], False
    for ln in merged:
        if ln == "":
            if not prev_empty: out.append("")
            prev_empty = True
        else:
            out.append(ln); prev_empty = False
    return "\n".join(out).strip()

def paragraphs(text: str) -> List[str]:
    paras = [p.strip() for p in text.split("\n\n")]
    return [p for p in paras if p]

def split_sentences(par: str) -> List[str]:
    segs = [s.strip() for s in SENT_SPLIT_RE.split(par)]
    out = []
    for s in segs:
        if not s: continue
        if len(s) > CHUNK_MAX:
            tmp = re.split(r"[，,、]\s*", s)
            for t in tmp:
                t = t.strip()
                if t: out.append(t)
        else:
            out.append(s)
    return out

def pack_chunks(sent_list: List[str]) -> List[str]:
    chunks, i = [], 0
    while i < len(sent_list):
        cur, cur_len = [], 0
        start = max(0, i - SENT_OVERLAP) if chunks and SENT_OVERLAP > 0 else i
        j = start
        while j < len(sent_list) and (cur_len < CHUNK_MAX or not cur):
            s = sent_list[j]
            add = len(s) + (1 if cur else 0)
            if cur_len + add <= CHUNK_MAX or not cur:
                cur.append(s); cur_len += add; j += 1
            else:
                break
        while j < len(sent_list) and cur_len < CHUNK_MIN:
            s = sent_list[j]; cur.append(s); cur_len += len(s) + 1; j += 1
        chunks.append("".join(cur))
        i = j
    uniq, seen = [], set()
    for c in chunks:
        if c not in seen:
            uniq.append(c); seen.add(c)
    return uniq

def keyword_tags(text: str) -> List[str]:
    tgs = set()
    pairs = [
        (r"(饮食|喂养|配方|食谱|营养)", "饮食"),
        (r"(疫苗|免疫|驱虫|体检|消毒)", "医疗"),
        (r"(梳理|清洁|洗澡|美容|掉毛)", "梳理"),
        (r"(训练|行为|社交|奖励|惩罚|习惯)", "训练"),
        (r"(常见病|症状|治疗|用药|就医)", "常见病"),
        (r"(禁忌|注意|安全|误食|危险)", "禁忌"),
        (r"(环境|居家|猫砂|犬舍|笼子|玩具)", "环境"),
        (r"(幼犬|幼猫|成犬|成猫|老年)", "阶段"),
    ]
    for pat, tag in pairs:
        if re.search(pat, text): tgs.add(tag)
    return sorted(tgs)

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode("utf-8")).hexdigest()

# ================ Milvus ================
def ensure_collection(client: MilvusClient):
    if client.has_collection(COLL_NAME):
        return
    schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=False)
    schema.add_field("id",            DataType.INT64,   is_primary=True)
    schema.add_field("species_id",    DataType.VARCHAR, max_length=64)
    schema.add_field("species_name",  DataType.VARCHAR, max_length=128)
    schema.add_field("node_type",     DataType.VARCHAR, max_length=20)
    schema.add_field("content",       DataType.VARCHAR, max_length=4096)
    schema.add_field("image_uri",     DataType.VARCHAR, max_length=1024)
    schema.add_field("image_hash",    DataType.VARCHAR, max_length=64)
    schema.add_field("tags",          DataType.VARCHAR, max_length=256)
    schema.add_field("embedding",     DataType.FLOAT_VECTOR, dim=DIM)
    # 注意：此处不建索引，等全部插入完成后再建
    client.create_collection(COLL_NAME, schema=schema)

def build_index_and_load(client: MilvusClient):
    idx = client.prepare_index_params()
    idx.add_index("embedding", index_type="AUTOINDEX", metric_type="COSINE", params={})
    client.create_index(COLL_NAME, index_params=idx)
    client.load_collection(COLL_NAME)

# ================ 断点状态 ================
def load_state() -> Dict[str, int]:
    if STATE_PATH.exists():
        try:
            return json.loads(STATE_PATH.read_text("utf-8"))
        except Exception:
            return {}
    return {}

def save_state(state: Dict[str, int]):
    STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

# ================ 嵌入（带重试、限长） ================
def embed_text(sess: requests.Session, text: str) -> Optional[List[float]]:
    txt = text[:EMBED_MAX_CHARS]  # 截断到保守长度
    for attempt in range(1, EMBED_MAX_RETRY + 1):
        try:
            r = sess.post(EMBED_API, json={"text": txt, "normalize": True}, timeout=EMBED_TIMEOUT)
            if r.ok:
                data = r.json()
                emb = data.get("embedding")
                if isinstance(emb, list) and len(emb) == DIM:
                    return emb
                raise RuntimeError(f"bad embedding shape: {type(emb)}")
            else:
                raise RuntimeError(f"embed http {r.status_code}: {r.text[:200]}")
        except Exception as e:
            sleep = min(2 ** (attempt - 1) * 0.5, 4.0)
            print(f"[WARN] embed failed (attempt {attempt}/{EMBED_MAX_RETRY}): {e}; sleep {sleep}s")
            time.sleep(sleep)
    return None  # 放弃该 chunk

# ================ 主流程 ================
_stop = False
def _handle_sigint(sig, frame):
    global _stop
    _stop = True
    print("\n[INFO] 捕获中断信号，安全退出中（会保存断点）...")

signal.signal(signal.SIGINT, _handle_sigint)
signal.signal(signal.SIGTERM, _handle_sigint)

def process_one_file(path: Path, client: MilvusClient, sess: requests.Session, resume_idx: int = 0) -> Tuple[int, int]:
    raw = read_txt(path)
    cleaned = clean_text(raw)
    paras = paragraphs(cleaned)
    sent: List[str] = []
    for p in paras:
        sent.extend(split_sentences(p))
    chunks = pack_chunks(sent)
    if not chunks:
        print(f"[SKIP] 无有效内容：{path.name}")
        return 0, 0

    slug = path.stem
    sp = guess_species(slug)
    species_id, species_name = sp["species_id"], sp["species_name"]

    seen_hash = set()
    inserted, skipped = 0, 0
    batch: List[Dict] = []
    total = len(chunks)

    for idx, c in enumerate(chunks):
        if _stop: break
        if idx < resume_idx:
            continue

        chash = sha1(species_id + "|" + c)
        if chash in seen_hash:
            skipped += 1
            continue
        seen_hash.add(chash)

        emb = embed_text(sess, c)
        if emb is None:
            print(f"[ERR] 嵌入失败，跳过 chunk#{idx} ({path.name})")
            skipped += 1
            continue

        tg = keyword_tags(c)
        tag_str = ",".join(tg + ["care"])

        batch.append({
            "species_id":   species_id,
            "species_name": species_name,
            "node_type":    "care_text",
            "content":      c[:4096],
            "image_uri":    "",
            "image_hash":   chash,
            "tags":         tag_str,
            "embedding":    emb,
        })

        if len(batch) >= INSERT_BATCH:
            client.insert(COLL_NAME, batch)
            client.flush(COLL_NAME)  # 减少内存峰值
            inserted += len(batch)
            batch.clear()
            time.sleep(SLEEP_BETWEEN_BATCH)

    if batch and not _stop:
        client.insert(COLL_NAME, batch)
        client.flush(COLL_NAME)
        inserted += len(batch)
        batch.clear()

    return inserted, total - inserted

def main():
    if not TXT_DIR.exists():
        print(f"[ERR] 目录不存在：{TXT_DIR}"); sys.exit(1)

    client = MilvusClient(uri=DB_URI)
    ensure_collection(client)

    files = sorted([p for p in TXT_DIR.glob("*.txt") if p.is_file()])
    if not files:
        print(f"[WARN] 未找到 txt：{TXT_DIR}")
        return

    state = load_state()
    sess = requests.Session()

    t0 = time.time()
    total_ins = 0
    total_skip = 0
    processed_files = 0

    try:
        for p in files:
            if _stop: break
            resume_idx = int(state.get(str(p), 0))
            print(f"[RUN] {p.name} (resume from chunk {resume_idx}) ...")

            ins, sk = process_one_file(p, client, sess, resume_idx=resume_idx)
            total_ins += ins
            total_skip += sk
            processed_files += 1

            # 该文件处理完成，记录为末尾
            state[str(p)] = 10**12  # 标记完成
            save_state(state)
            print(f"[OK ] {p.name} -> inserted={ins}, skipped={sk}")
    finally:
        # 统一建索引 & 加载（仅在非中断且至少插入过时执行更合适）
        if not _stop and total_ins > 0:
            print("[INFO] 构建索引并加载 ...（这一步会花些时间/IO）")
            build_index_and_load(client)

    dt = time.time() - t0
    print(f"\n[DONE] 文件数={processed_files} | 成功 chunks={total_ins} | 跳过/失败={total_skip} | 用时={dt:.1f}s"
          + (" | (安全中断)" if _stop else ""))

if __name__ == "__main__":
    main()
