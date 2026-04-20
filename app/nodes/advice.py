# app/nodes/advice.py
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from app.prompts.advice_prompts import advice_prompt_template


def advice_node(state: AgentState) -> Dict[str, Any]:
    """
    行动建议节点 (Advice Node)
    处理用户寻求建议、规划、出谋划策的需求。
    """
    messages = state.get("messages", [])
    user_input = messages[-1].content
    chat_history = messages[:-1] if len(messages) > 1 else []

    intimacy = state.get("intimacy_level", 30)
    mood = state.get("companion_mood", "认真")
    shared_memories = state.get("shared_memories", [])
    # 提建议需要严密的逻辑和客观性，temperature 调低到 0.3
    llm = get_llm(temperature=0.3)
    structured_llm = llm.with_structured_output(CompanionResponse)
    chain = advice_prompt_template | structured_llm

    try:
        response: CompanionResponse = chain.invoke({
            "intimacy_level": intimacy,
            "companion_mood": mood,
            "shared_memories": shared_memories,
            "chat_history": chat_history,
            "user_input": user_input
        })

        print(f"📋 [灵犀规划内心戏]: {response.internal_monologue}")

        # 提供有价值的建议通常能稳定提升好感
        delta = response.intimacy_delta
        new_intimacy = max(-100, min(100, intimacy + delta))

        return {
            "messages": [AIMessage(content=response.reply_text)],
            "companion_mood": response.new_mood,
            "intimacy_level": new_intimacy
        }
    except Exception as e:
        print(f"⚠️ 建议节点生成失败: {e}")
        return {
            "messages": [AIMessage(content="这个问题有点复杂，给我一点时间查查资料再帮你参考好不好？")],
            "companion_mood": "认真"
        }
