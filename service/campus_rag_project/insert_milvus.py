import os
import re
import time
import glob
from typing import List, Dict, Optional

import numpy as np
from pymilvus import MilvusClient, DataType
from FlagEmbedding import BGEM3FlagModel

# ======== 配置区 ========
# 使用 Milvus Lite：给一个本地文件路径即可（不存在会自动创建）
LITE_DB_PATH = os.getenv("MILVUS_DB_PATH", "/home/wmy/workspace/server/campus_rag_project/milvus_lite.db")
COLLECTION = "jmu_pdf_pages_bge_m3"

# 目录与来源
TXT_DIR = "/home/wmy/workspace/server/campus_rag_project/data/txt_data"
SUM_DIR = "/home/wmy/workspace/server/campus_rag_project/data/summary_data"
SOURCE  = "2025新生入学手册.pdf"  # 用于拼主键与检索

# 向量模型（BGE-M3）
EMBED_MODEL_NAME = "/home/wmy/workspace/model_zoo/BAAI/bge-m3"
EMBED_DIM = 1024
BGE_BATCH_SIZE = 12
BGE_MAX_LENGTH = 4096  # 如不需要很长上下文可适当调小，加速编码

# 度量方式
METRIC_TYPE = "COSINE"

# ======== 工具函数 ========
def ensure_collection(client: MilvusClient):
    if client.has_collection(COLLECTION):
        print(f"[info] collection '{COLLECTION}' already exists.")
        client.load_collection(COLLECTION)
        return

    schema = client.create_schema(
        auto_id=False,
        enable_dynamic_field=False,
    )
    schema.add_field("id", DataType.VARCHAR, is_primary=True, max_length=128)
    schema.add_field("source", DataType.VARCHAR, max_length=256)
    schema.add_field("page_no", DataType.INT64)
    schema.add_field("path_txt", DataType.VARCHAR, max_length=512)
    schema.add_field("path_summary", DataType.VARCHAR, max_length=512)
    schema.add_field("title", DataType.VARCHAR, max_length=256)
    schema.add_field("text", DataType.VARCHAR, max_length=65535)
    schema.add_field("summary", DataType.VARCHAR, max_length=65535)
    schema.add_field("vector", DataType.FLOAT_VECTOR, dim=EMBED_DIM)
    schema.add_field("created_at_ms", DataType.INT64)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="vector",
        index_type="FLAT",
        metric_type=METRIC_TYPE,
        params={},
    )

    client.create_collection(
        collection_name=COLLECTION,
        schema=schema,
        index_params=index_params,
        enable_dynamic_field=False,
    )
    client.load_collection(COLLECTION)
    print(f"[ok] collection '{COLLECTION}' created & loaded (Milvus Lite).")


def read_text(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        return f.read().strip()


def extract_title(summary_text: str) -> Optional[str]:
    # 取首个 '# ' 标题作为 title（如存在）
    for line in summary_text.splitlines():
        if line.strip().startswith("# "):
            return line.strip().lstrip("# ").strip()
    return None


def extract_abstract(summary_text: str) -> Optional[str]:
    """
    从摘要文件中抽取“总摘要”段落。适配格式：
    ## 总摘要（200-300字）
    <内容...>
    ## 要点列表
    """
    pattern = r"^##\s*总摘要[^\n]*\n+([\s\S]*?)(?=\n##\s*|\Z)"
    m = re.search(pattern, summary_text, flags=re.MULTILINE)
    if m:
        abstract = m.group(1).strip()
        return abstract
    # 兜底：如果没有明确“总摘要”小节，就取全文的首段
    paras = [p.strip() for p in re.split(r"\n\s*\n", summary_text) if p.strip()]
    return paras[0] if paras else None


def basename_without_ext(p: str) -> str:
    return os.path.splitext(os.path.basename(p))[0]


def parse_page_no(basename: str) -> int:
    """
    从类似 '-03' 或 '03' 或 'page-03' 中提取页码数字；失败则返回 -1
    """
    m = re.search(r"(\d+)", basename)
    return int(m.group(1)) if m else -1


def build_doc_id(source: str, page_no: int) -> str:
    return f"{source}::{page_no:03d}" if page_no >= 0 else f"{source}::{basename_without_ext(source)}"


def chunked(iterable, size=512):
    buf = []
    for x in iterable:
        buf.append(x)
        if len(buf) >= size:
            yield buf
            buf = []
    if buf:
        yield buf


def l2_normalize(vec: np.ndarray) -> np.ndarray:
    """确保用于 COSINE 的向量为单位长度。"""
    if vec.ndim == 1:
        vec = vec[None, :]
    norms = np.linalg.norm(vec, axis=1, keepdims=True) + 1e-12
    return vec / norms


# ======== 主流程 ========
def main():
    # 0) 确保 Lite DB 目录存在
    db_dir = os.path.dirname(LITE_DB_PATH)
    if db_dir and not os.path.exists(db_dir):
        os.makedirs(db_dir, exist_ok=True)

    # 1) 连接 Milvus Lite（传本地文件路径）
    client = MilvusClient(LITE_DB_PATH)
    ensure_collection(client)

    # 2) 准备 BGE-M3 模型
    bge = BGEM3FlagModel(
        EMBED_MODEL_NAME,
        use_fp16=True,            # 4090/3090 等显卡可开启以加速；CPU 环境会自动回退
        normalize_embeddings=False # 我们手动做 L2 归一化，避免不同版本行为差异
    )
    print(f"[ok] BGE-M3 loaded from: {EMBED_MODEL_NAME}")

    # 3) 遍历 txt 目录，匹配对应的 *_summary.txt
    txt_files = sorted(glob.glob(os.path.join(TXT_DIR, "*.txt")))
    print(f"[info] found txt files: {len(txt_files)}")

    rows: List[Dict] = []
    now_ms = int(time.time() * 1000)

    for txt_path in txt_files:
        base = basename_without_ext(txt_path)  # e.g., '-03'
        sum_path = os.path.join(SUM_DIR, f"{base}_summary.txt")
        if not os.path.exists(sum_path):
            print(f"[warn] summary not found for {base}: {sum_path}")
            continue

        # 读取原文与摘要
        raw_text = read_text(txt_path)
        sum_text = read_text(sum_path)

        # 解析标题与“总摘要”
        title = extract_title(sum_text) or ""
        abstract = extract_abstract(sum_text)
        if not abstract:
            print(f"[warn] no abstract extracted, skip: {sum_path}")
            continue

        # 计算向量（用“总摘要”）
        try:
            out = bge.encode(
                [abstract],
                batch_size=BGE_BATCH_SIZE,
                max_length=BGE_MAX_LENGTH,
            )
            dense = out["dense_vecs"]
            if isinstance(dense, list):
                dense = np.array(dense, dtype=np.float32)
            dense = l2_normalize(dense).astype(np.float32)  # 归一化 + 保证 float32
            vec = dense[0]
        except Exception as e:
            print(f"[error] BGE encode failed for {base}: {e}")
            continue

        if vec.shape[0] != EMBED_DIM:
            print(f"[error] embedding dim mismatch: got {vec.shape[0]} expect {EMBED_DIM}, skip {base}")
            continue

        page_no = parse_page_no(base)
        doc_id = build_doc_id(SOURCE, page_no)

        row = {
            "id": doc_id,
            "source": SOURCE,
            "page_no": int(page_no),
            "path_txt": txt_path,
            "path_summary": sum_path,
            "title": title,
            "text": raw_text,
            "summary": abstract,
            "vector": vec.tolist(),
            "created_at_ms": now_ms,
        }
        rows.append(row)

    if not rows:
        print("[warn] no rows to insert.")
        return

    # 4) 批量入库
    total = 0
    for batch in chunked(rows, size=256):
        client.insert(collection_name=COLLECTION, data=batch)
        total += len(batch)
    client.flush(COLLECTION)
    client.load_collection(COLLECTION)

    print(f"[ok] inserted {total} rows into '{COLLECTION}' (Milvus Lite @ {LITE_DB_PATH}).")

    # 5) 快速检索验证：查询同样用 BGE 编码并做 L2 归一化
    try:
        q = "集美大学校歌"
        q_out = bge.encode([q], batch_size=1, max_length=512)
        q_dense = q_out["dense_vecs"]
        if isinstance(q_dense, list):
            q_dense = np.array(q_dense, dtype=np.float32)
        q_vec = l2_normalize(q_dense).astype(np.float32)[0].tolist()

        res = client.search(
            collection_name=COLLECTION,
            data=[q_vec],
            limit=5,
            output_fields=["id", "source", "page_no", "title", "path_txt"],
            search_params={"metric_type": METRIC_TYPE},
        )
        print("[demo] top hits for query:", q)
        for i, hit in enumerate(res[0]):
            ent = hit["entity"]
            print(f"  {i+1}. id={ent['id']}, page={ent['page_no']}, title={ent['title']}")
    except Exception as e:
        print(f"[warn] search demo failed: {e}")


if __name__ == "__main__":
    main()
