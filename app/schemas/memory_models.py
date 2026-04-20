# app/schemas/memory_models.py
from pydantic import BaseModel, Field
from typing import List


class MemoryItem(BaseModel):
    """单条被淬炼的记忆"""
    room_category: str = Field(
        description="记忆所属房间，必须是: 'preferences'(客观偏好事实), 'romance_diary'(情感互动日记), 'study_progress'(学习进度)")
    compressed_content: str = Field(description="高度压缩的记忆内容 (如: '严重海鲜过敏', '4.20因前女友话题冷战')")
    importance_score: int = Field(description="重要程度 1-10。低于5分的日常废话(如吃了么)将被系统丢弃")


class MemoryExtraction(BaseModel):
    """记忆提取的结构化输出"""
    extracted_memories: List[MemoryItem] = Field(description="本次对话提取出的所有高价值记忆,你的输出要符合这个格式")
