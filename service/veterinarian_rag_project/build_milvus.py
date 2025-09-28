# create_pet_kb_lite.py
# pip install "pymilvus>=2.5.0"

from pymilvus import MilvusClient, DataType

# === 使用 Milvus Lite：把 uri 设为本地文件即可（自动在本地创建/使用该 DB 文件） ===
# 例如 "./petkb.db"；路径可换成绝对路径
client = MilvusClient(uri="./petkb.db")

COLLECTION = "pet_knowledge_base"
DIM = 1024  # jina-clip-v2 向量维度

# 如果已存在且想重建，先删除：
if client.has_collection(COLLECTION):
    client.drop_collection(COLLECTION)

# 1) 自定义 Schema（关闭动态字段，全部字段显式定义）
schema = MilvusClient.create_schema(
    auto_id=True,                # 主键自增
    enable_dynamic_field=False,  # 关闭 $meta
)

# 2) 添加字段（与你的最终设计一致）
schema.add_field("id",             DataType.INT64,    is_primary=True)
schema.add_field("species_id",     DataType.VARCHAR,  max_length=64)
schema.add_field("species_name",   DataType.VARCHAR,  max_length=128)
schema.add_field("node_type",      DataType.VARCHAR,  max_length=20)     # "image" | "introduction_text" | "care_text"
schema.add_field("content",        DataType.VARCHAR,  max_length=4096)   # 文本内容
schema.add_field("image_uri",      DataType.VARCHAR,  max_length=1024)   # 图片路径/URL（不建议存原图base64）
schema.add_field("image_hash",     DataType.VARCHAR,  max_length=64)     # 可选去重/缓存键
schema.add_field("tags",           DataType.VARCHAR,  max_length=256)    # 主题标签
schema.add_field("embedding",      DataType.FLOAT_VECTOR, dim=DIM)       # 统一用 CLIP 向量

# 3) 索引参数（向量字段）
#   - Lite 下推荐用 AUTOINDEX（自动选择合适的近邻结构）
#   - metric 用 COSINE（配合向量 L2 归一化或 encode(normalize_embeddings=True)）
index_params = client.prepare_index_params()
index_params.add_index(
    field_name="embedding",
    index_type="AUTOINDEX",
    metric_type="COSINE",
    params={"nlist": 1024}  # 可留空；给出也不会出错（AUTOINDEX会自适配）
)

# 4) 创建集合（会自动建索引并加载）
client.create_collection(
    collection_name=COLLECTION,
    schema=schema,
    index_params=index_params,
)

print(f"[OK] Created collection '{COLLECTION}' in Milvus Lite DB './petkb.db'")
