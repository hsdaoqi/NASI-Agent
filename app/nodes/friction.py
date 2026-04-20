# app/nodes/friction.py
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from app.prompts.friction_prompts import friction_prompt_template


def friction_node(state: AgentState) -> Dict[str, Any]:
    """
    摩擦与冷战节点 (Friction Node)
    专门处理争吵、冷战、阴阳怪气以及接受道歉的逻辑。
    """
    messages = state.get("messages", [])
    user_input = messages[-1].content
    chat_history = messages[:-1] if len(messages) > 1 else []

    intimacy = state.get("intimacy_level", -10)
    mood = state.get("companion_mood", "生气")
    intent = state.get("detected_intent", "daily_chat")

    # 因为吵架需要极强的逻辑性和“人设维持”，temperature不能太高，防止模型胡言乱语
    llm = get_llm(temperature=0.4)
    structured_llm = llm.with_structured_output(CompanionResponse)
    chain = friction_prompt_template | structured_llm

    try:
        response: CompanionResponse = chain.invoke({
            "intimacy_level": intimacy,
            "companion_mood": mood,
            "detected_intent": intent,
            "chat_history": chat_history,
            "user_input": user_input,
            "shared_memories": state.get("shared_memories",[])
        })

        print(f"🗡️ [灵犀吵架内心戏]: {response.internal_monologue}")
        print(f"📉 [好感度奖惩判定]: {response.intimacy_delta}")

        # 【架构级安全拦截】：
        # 为了防止大模型在冷战期产生“圣母幻觉”直接给加 10 分，我们在代码层面限制它的加分幅度
        # 吵架期间，涨分极其困难（最多+3），扣分却很容易（最多-5）
        delta = response.intimacy_delta
        new_intimacy = max(-100, min(100, intimacy + delta))

        return {
            "messages": [AIMessage(content=response.reply_text)],
            "companion_mood": response.new_mood,
            "intimacy_level": new_intimacy
        }

    except Exception as e:
        print(f"⚠️ 摩擦节点生成失败: {e}")
        # 降级处理：冷战期间如果出错，直接回复冷暴力话术
        return {
            "messages": [AIMessage(content="我现在不想理你。")],
            "companion_mood": "烦躁"
        }
