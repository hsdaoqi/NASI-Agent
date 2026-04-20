# app/nodes/empathy.py
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from app.prompts.empathy_prompts import empathy_prompt_template


def empathy_node(state: AgentState) -> Dict[str, Any]:
    """
    共情节点 (Empathy Node)
    处理用户的情绪低落、压力、焦虑，提供极高价值的情绪慰藉。
    """
    messages = state.get("messages", [])
    user_input = messages[-1].content
    chat_history = messages[:-1] if len(messages) > 1 else []

    intimacy = state.get("intimacy_level", 30)
    mood = state.get("companion_mood", "心疼")
    user_emo_intensity = state.get("emotion_intensity", 5)

    # 安抚需要细腻和稳定，温度设为 0.5
    llm = get_llm(temperature=0.5)
    structured_llm = llm.with_structured_output(CompanionResponse)
    chain = empathy_prompt_template | structured_llm

    try:
        response: CompanionResponse = chain.invoke({
            "intimacy_level": intimacy,
            "companion_mood": mood,
            "chat_history": chat_history,
            "user_input": user_input,
            "shared_memories": state.get("shared_memories",[])
        })

        print(f"🌊 [灵犀治愈内心戏]: {response.internal_monologue}")

        # 安抚是极佳的亲密度提升机会。
        # 如果用户情绪强度很高（很痛苦），而灵犀接住了，亲密度会大幅提升。

        delta = response.intimacy_delta
        new_intimacy = max(-100, min(100, intimacy + delta))

        return {
            "messages": [AIMessage(content=response.reply_text)],
            "companion_mood": response.new_mood,
            "intimacy_level": new_intimacy
        }

    except Exception as e:
        print(f"⚠️ 共情节点生成失败: {e}")
        return {
            "messages": [AIMessage(content="*抱住你* 乖，我在呢，我会一直陪着你的。")],
            "companion_mood": "心疼"
        }
