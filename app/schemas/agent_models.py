from enum import Enum
from pydantic import BaseModel, Field


class IntentType(str, Enum):
    DAILY_CHAT = "daily_chat"  # 日常闲聊/贴贴
    EMOTIONAL_SUPPORT = "emo_support"  # 情感慰藉（当你难过时）
    DEEP_TALK = "deep_talk"  # 深度交心（探讨价值观/未来）
    LIFE_PLANNER = "life_planner"  # 贤内助（给建议/做规划）
    CRISIS = "crisis"  # 危机干预
    RELATIONSHIP_FRICTION = "relationship_friction"
    FLIRT_TEASE = 'flirt_tease'
    ANGRY = 'angry'
    # 督学/背单词意图
    STUDY_MOMO = "study_momo"


class IntentClassification(BaseModel):
    """虚拟伴侣对用户意图的敏锐感知"""
    intent: IntentType = Field(description="感知到的用户核心交互意图，各自含义：")
    user_emotion: str = Field(description="识别到的用户当前情绪关键词，如开心，悲伤，愤怒，无聊，平静")
    emotion_intensity: int = Field(description="用户情绪强度 必须要是 1-10 的 int 类型的正整数", ge=1, le=10)
    intimacy_delta: int = Field(description="本次对话对亲密度的潜在影响值 (-5 到 +5)")
    reasoning: str = Field(description="为什么这样分类的逻辑分析")


class CompanionResponse(BaseModel):
    """虚拟伴侣的综合回复模型：不仅包含说的话，还包含她的内部状态更新"""
    reply_text: str = Field(description="你（灵犀）发给用户的文本消息，必须符合你当前的心情和亲密度设定")
    new_mood: str = Field(description="回复完这句话后，你（灵犀）的心情变成了什么？(例如：开心、害羞、小确幸、还在生气、吃醋)")
    intimacy_delta: int = Field(description="本次互动后亲密度的增减值（通常在 -5 到 +5 之间，如果他惹你生气可能是负数）")
    internal_monologue: str = Field(description="你心里的潜台词（内心戏，不需要发给用户，用于丰富人设逻辑）")
