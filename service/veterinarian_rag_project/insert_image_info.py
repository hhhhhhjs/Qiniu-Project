# ingest_pet_kb_lite.py
# =========================================
# 把图文数据写入 Milvus Lite（单集合 pet_knowledge_base）
# 目录结构举例：
# /.../data/pet/pictures/dog/拉布拉多/*.jpg + info.txt(或*.txt)
# /.../data/pet/pictures/cat/英短/*.jpg + *.txt
# =========================================

import os
import sys
import glob
import json
import time
import hashlib
import requests
from typing import List, Dict, Tuple

from pymilvus import MilvusClient, DataType

# ============ 配置 ============
ROOT_DIR = "/home/wmy/workspace/server/veterinarian_rag_project/data/pet/pictures"
EMBED_BASE = "http://127.0.0.1:9200"  # 你的 embedding 服务
DB_URI = "./petkb.db"                 # Milvus Lite DB 文件
COLLECTION = "pet_knowledge_base"
DIM = 1024

ANIMALS = ["dog", "cat"]  # 两个一级目录
IMG_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}

# ============ Milvus Lite ============

def ensure_collection(client: MilvusClient):
    if client.has_collection(COLLECTION):
        print(f"[OK] collection exists: {COLLECTION}")
        return

    schema = MilvusClient.create_schema(auto_id=True, enable_dynamic_field=False)
    schema.add_field("id",            DataType.INT64,   is_primary=True)
    schema.add_field("species_id",    DataType.VARCHAR, max_length=64)
    schema.add_field("species_name",  DataType.VARCHAR, max_length=128)
    schema.add_field("node_type",     DataType.VARCHAR, max_length=20)     # "image" | "introduction_text" | "care_text"
    schema.add_field("content",       DataType.VARCHAR, max_length=4096)   # 文本内容
    schema.add_field("image_uri",     DataType.VARCHAR, max_length=1024)   # 图片路径
    schema.add_field("image_hash",    DataType.VARCHAR, max_length=64)     # sha1
    schema.add_field("tags",          DataType.VARCHAR, max_length=256)    # 主题或 animal 标签
    schema.add_field("embedding",     DataType.FLOAT_VECTOR, dim=DIM)

    index_params = client.prepare_index_params()
    index_params.add_index(
        field_name="embedding",
        index_type="AUTOINDEX",       # Lite 推荐
        metric_type="COSINE",
        params={}                     # 让 Lite 自适应
    )

    client.create_collection(
        collection_name=COLLECTION,
        schema=schema,
        index_params=index_params,
    )
    print(f"[OK] created collection: {COLLECTION}")

# ============ 嵌入 API ============

def embed_pair(text: str, image_path: str) -> Tuple[List[float], List[float]]:
    """同时拿到文本和该图像的向量"""
    payload = {"text": text, "image": image_path, "normalize": True}
    r = requests.post(f"{EMBED_BASE}/v1/embed/pair", json=payload, timeout=120)
    if not r.ok:
        raise RuntimeError(f"pair embed failed: {r.text}")
    data = r.json()
    return data["text_embedding"], data["image_embedding"]

def embed_image(image_path: str) -> List[float]:
    payload = {"image": image_path, "normalize": True}
    r = requests.post(f"{EMBED_BASE}/v1/embed/image", json=payload, timeout=120)
    if not r.ok:
        raise RuntimeError(f"image embed failed: {image_path} -> {r.text}")
    return r.json()["embedding"]

# ============ 文件扫描与工具 ============

def list_species_dirs(root_dir: str, animals: List[str]) -> List[Tuple[str, str]]:
    """
    返回 [(animal, species_dir_abs), ...]
    species_dir_abs 形如 /.../pictures/dog/拉布拉多
    """
    out = []
    for a in animals:
        base = os.path.join(root_dir, a)
        if not os.path.isdir(base):
            print(f"[Warn] not a dir: {base}")
            continue
        for name in sorted(os.listdir(base)):
            d = os.path.join(base, name)
            if os.path.isdir(d):
                out.append((a, d))
    return out

def pick_text_file(species_dir: str) -> str:
    # 按你的描述：每类只有一个 txt。尝试 *.txt 或 info.txt
    cand = glob.glob(os.path.join(species_dir, "*.txt"))
    if not cand:
        return ""
    # 优先 info.txt
    for p in cand:
        if os.path.basename(p).lower() in ("info.txt", "intro.txt", "introduction.txt"):
            return p
    # 取第一个
    return cand[0]

def read_text_file(path: str) -> str:
    if not path:
        return ""
    for enc in ("utf-8", "utf-8-sig", "gb18030"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read().strip()
        except Exception:
            continue
    # 最后兜底二进制解码
    with open(path, "rb") as f:
        raw = f.read()
    try:
        return raw.decode("utf-8", errors="ignore").strip()
    except Exception:
        return ""

def list_images(species_dir: str) -> List[str]:
    files = []
    for fn in sorted(os.listdir(species_dir)):
        p = os.path.join(species_dir, fn)
        if os.path.isfile(p) and os.path.splitext(fn)[1].lower() in IMG_EXTS:
            files.append(p)
    return files

def sha1_of_file(path: str) -> str:
    h = hashlib.sha1()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()

def make_species_id(animal: str, species_name_dir: str) -> str:
    # 保留中文更直观，同时加 animal 前缀避免同名冲突
    safe = species_name_dir.replace(" ", "_").replace("/", "_")
    return f"{animal}_{safe}"

# ============ 写库 ============

def insert_rows(client: MilvusClient, rows: List[Dict]):
    if not rows:
        return
    # MilvusClient 支持 list[dict]
    client.insert(collection_name=COLLECTION, data=rows)

def ingest_one_species(client: MilvusClient, animal: str, species_dir: str):
    species_name = os.path.basename(species_dir)  # 目录名作为品种中文名
    species_id = make_species_id(animal, species_name)

    # 文本：只存一次
    txt_path = pick_text_file(species_dir)
    intro_text = read_text_file(txt_path)
    if not intro_text:
        # 若确实没有文本，就用 species_name 兜底，避免空文本检索效果不稳定
        intro_text = species_name

    # 图片：全部入库
    images = list_images(species_dir)
    if not images:
        print(f"[Skip] no images: {species_dir}")
        return

    # 选第一张作为“代表图”，和文本一起调用 /v1/embed/pair（更稳定）
    rep_img = images[0]
    try:
        text_emb, rep_img_emb = embed_pair(intro_text, rep_img)
    except Exception as e:
        print(f"[Error] pair embed failed for {species_dir}: {e}")
        return

    rows = []

    # A) 文本节点（只一次）
    rows.append({
        "species_id":   species_id,
        "species_name": species_name,
        "node_type":    "introduction_text",
        "content":      intro_text,
        "image_uri":    "",                  # 文本节点无需图片
        "image_hash":   "",
        "tags":         animal,              # 标记 dog/cat
        "embedding":    text_emb,
    })

    # B) 代表图节点（第一张）
    rows.append({
        "species_id":   species_id,
        "species_name": species_name,
        "node_type":    "image",
        "content":      "",                  # 建议图片节点 content 为空；如需也可填 intro_text
        "image_uri":    rep_img,
        "image_hash":   sha1_of_file(rep_img),
        "tags":         f"{animal},代表图",
        "embedding":    rep_img_emb,
    })

    # C) 其余图片
    for p in images[1:]:
        try:
            emb = embed_image(p)
        except Exception as e:
            print(f"[Warn] image embed failed: {p} -> {e}")
            continue
        rows.append({
            "species_id":   species_id,
            "species_name": species_name,
            "node_type":    "image",
            "content":      "",
            "image_uri":    p,
            "image_hash":   sha1_of_file(p),
            "tags":         animal,
            "embedding":    emb,
        })

    insert_rows(client, rows)
    print(f"[OK] inserted: {species_name} ({animal}) | text:1, images:{len(images)}")

def main():
    # 1) 连接 Milvus Lite
    client = MilvusClient(uri=DB_URI)
    ensure_collection(client)

    # 2) 遍历 dog/cat 两类
    t0 = time.time()
    species_dirs = list_species_dirs(ROOT_DIR, ANIMALS)
    print(f"[Info] found {len(species_dirs)} species dirs")

    n_ok = 0
    for animal, d in species_dirs:
        try:
            ingest_one_species(client, animal, d)
            n_ok += 1
        except KeyboardInterrupt:
            raise
        except Exception as e:
            print(f"[Error] ingest failed for {d}: {e}")

    dt = time.time() - t0
    print(f"[Done] species processed: {n_ok}/{len(species_dirs)} in {dt:.1f}s")

if __name__ == "__main__":
    main()
