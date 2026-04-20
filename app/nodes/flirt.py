# app/nodes/flirt.py
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from app.prompts.flirt_prompts import flirt_prompt_template


def flirt_node(state: AgentState) -> Dict[str, Any]:
    """
    调情与拉扯节点 (Flirt Node)
    处理暧昧、推拉、吃醋等高张力互动。
    """
    messages = state.get("messages", [])
    user_input = messages[-1].content
    chat_history = messages[:-1] if len(messages) > 1 else []

    intimacy = state.get("intimacy_level", 30)
    mood = state.get("companion_mood", "害羞")

    # 调情需要高创造力和不可预测性，温度设为 0.8
    llm = get_llm(temperature=0.8)
    structured_llm = llm.with_structured_output(CompanionResponse)
    chain = flirt_prompt_template | structured_llm

    try:
        response: CompanionResponse = chain.invoke({
            "intimacy_level": intimacy,
            "companion_mood": mood,
            "chat_history": chat_history,
            "user_input": user_input,
            "shared_memories": state.get("shared_memories",[])
        })

        print(f"💋 [灵犀调情内心戏]: {response.internal_monologue}")
        print(f"📈 [心动指数变化]: {response.intimacy_delta}")

        # 调情如果成功，亲密度加成较高；如果玩脱了（比如开玩笑过火）也可能扣分
        # 限制单次心动幅度在 -3 到 +5 之间
        delta = max(-3, min(5, response.intimacy_delta))
        new_intimacy = max(-100, min(100, intimacy + delta))

        return {
            "messages": [AIMessage(content=response.reply_text)],
            "companion_mood": response.new_mood,
            "intimacy_level": new_intimacy
        }

    except Exception as e:
        print(f"⚠️ 调情节点生成失败: {e}")
        # 降级处理：害羞不知所措
        return {
            "messages": [AIMessage(content="哎呀...你突然这么说，我都不知道该怎么接了呀。*脸红*")],
            "companion_mood": "害羞"
        }
