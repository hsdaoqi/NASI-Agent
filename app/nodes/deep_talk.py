# app/nodes/deep_talk.py
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from app.prompts.deep_talk_prompts import deep_talk_prompt_template


def deep_talk_node(state: AgentState) -> Dict[str, Any]:
    """
    灵魂交心节点 (Deep Talk Node)
    处理深刻对话、价值观碰撞和认知引导。
    """
    messages = state.get("messages", [])
    user_input = messages[-1].content
    # 如果有脱敏逻辑，确保这里提取的是 chat_history
    chat_history = messages[:-1] if len(messages) > 1 else []

    intimacy = state.get("intimacy_level", 30)
    mood = state.get("companion_mood", "专注")

    # 深度对话需要平衡创造力与逻辑严谨性，temperature 设为 0.6
    llm = get_llm(temperature=0.6)
    structured_llm = llm.with_structured_output(CompanionResponse)
    chain = deep_talk_prompt_template | structured_llm

    try:
        response: CompanionResponse = chain.invoke({
            "intimacy_level": intimacy,
            "companion_mood": mood,
            "shared_memories": state.get("shared_memories",[]),  # 后续可接入真实记忆
            "chat_history": chat_history,
            "user_input": user_input
        })

        print(f"🌌 [灵犀思考内心戏]: {response.internal_monologue}")
        print(f"🔗 [精神契合度变化]: {response.intimacy_delta}")

        # 深度交心是建立长期羁绊的最强手段
        # 如果聊得好，可以突破日常聊天的加分上限 (比如允许加 3-5 分)
        delta = response.intimacy_delta
        new_intimacy = max(-100, min(100, intimacy + delta))

        return {
            "messages": [AIMessage(content=response.reply_text)],
            "companion_mood": response.new_mood,
            "intimacy_level": new_intimacy
        }

    except Exception as e:
        print(f"⚠️ 深度交心节点生成失败: {e}")
        # 降级处理
        return {
            "messages": [AIMessage(content="这个问题好深奥呀，我得好好想一想才能回答你。")],
            "companion_mood": "若有所思"
        }
