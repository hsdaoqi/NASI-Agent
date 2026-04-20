from typing import TypedDict, Annotated, Sequence, List
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """虚拟伴侣全局状态机 (V3 双轴虐恋版)"""

    # --- 1. 基础记忆流 ---
    # add_messages 确保每次对话都被追加，而不是覆盖
    messages: Annotated[Sequence[BaseMessage], add_messages]

    # --- 2. 用户侧状态 (由 state_tracker_node 更新) ---
    user_emotion: str  # 用户当前情绪关键词 (如：疲惫、愤怒、开心)
    emotion_intensity: int  # 用户情绪激烈程度 (1-10)
    detected_intent: str  # 用户核心意图 (如：flirt_tease, apology, daily_chat)

    # --- 3. 伴侣侧状态 (由各执行节点如 daily_chat_node 更新) ---
    # 【核心重构】亲密度范围变为 -100 到 100
    intimacy_level: int
    companion_mood: str  # 她的心情状态 (如：小确幸、吃醋、心灰意冷)

    # --- 4. 长期图谱记忆 (由 Memory 模块提取注入) ---
    shared_memories: List[str]
    user_preferences: List[str]

    # --- 5. 安全与熔断 ---
    crisis_alert_level: int  # 0=安全, 1=疑似, 2=高危
    # 个人人信息
    momo_token: str
    user_id: str
