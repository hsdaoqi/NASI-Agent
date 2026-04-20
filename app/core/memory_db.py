# app/core/memory_db.py
import chromadb
import uuid
from chromadb.config import Settings
from chromadb.utils import embedding_functions

# 1. 初始化持久化客户端（数据会存在本地的 ./chroma_data 文件夹里，重启不丢）
# 生产环境中可以换成 chromadb.HttpClient 连接独立的云服务器
chroma_client = chromadb.PersistentClient(path="./chroma_data")
huggingface_ef = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="BAAI/bge-small-zh-v1.5"
)
# 2. 建立你的“记忆宫殿”房间 (Collections)
# Chroma 默认会使用轻量级的本地 embedding 模型把文字变成向量
room_preferences = chroma_client.get_or_create_collection(
    name="room_preferences",
    embedding_function=huggingface_ef,
    metadata={"hnsw:space": "cosine"}
)
room_romance_diary = chroma_client.get_or_create_collection(
    name="room_romance_diary",
    embedding_function=huggingface_ef,
    metadata={"hnsw:space": "cosine"}
)
room_study_progress = chroma_client.get_or_create_collection(
    name="room_study_progress",
    embedding_function=huggingface_ef,
    metadata={"hnsw:space": "cosine"}
)


def get_room_collection(room_name: str):
    """根据名称获取对应的房间"""
    rooms = {
        "preferences": room_preferences,
        "romance_diary": room_romance_diary,
        "study_progress": room_study_progress
    }
    return rooms.get(room_name)


def generate_id() -> str:
    return str(uuid.uuid4())
