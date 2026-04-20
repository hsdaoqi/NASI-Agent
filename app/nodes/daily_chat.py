from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from app.prompts.chat_prompts import chat_prompt_template
from app.tools.agent_tools import base_tools


def daily_chat_node(state: AgentState) -> Dict[str, Any]:
    """
    日常闲聊节点：在关系正常(亲密度>=0)时，处理聊天，并动态改变灵犀自己的心情和好感度。
    """
    messages = state.get("messages", [])
    # 提取关系底座数据
    intimacy = state.get("intimacy_level", 0)
    mood = state.get("companion_mood", "平静")

    # 闲聊需要人设感，temperature 稍高以增加文本多样性
    llm = get_llm(temperature=0.5).with_config({"request_timeout": 10.0})
    llm_with_tools = llm.bind_tools(base_tools + [CompanionResponse])
    chain = chat_prompt_template | llm_with_tools

    try:
        # LLM 根据当前亲密度和心情，生成回复和后续的心理状态
        response: CompanionResponse = chain.invoke({
            "intimacy_level": intimacy,
            "companion_mood": mood,
            "shared_memories": state.get("shared_memories", []),
            "chat_history": messages[:-1],
            "user_input": messages[-1].content
        })

        print(f"💭 [灵犀内心戏]: {response.internal_monologue}")
        print(f"💓 [心情转变]: 从 '{mood}' 变成了 '{response.new_mood}'")

        # 【核心计算】限制亲密度在 -100 到 100 之间
        new_intimacy = max(-100, min(100, intimacy + response.intimacy_delta))
        print(f"📊 [亲密度变化]: {intimacy} -> {new_intimacy}")

        # 返回更新字典：新增一条 AI 消息，并覆盖心情和亲密度
        return {
            "messages": [AIMessage(content=response.reply_text)],
            "companion_mood": response.new_mood,
            "intimacy_level": new_intimacy
        }

    except Exception as e:
        print(f"⚠️ 生成闲聊回复失败: {e}")
        return {
            "messages": [AIMessage(content="哎呀，我刚刚走神了，没听清你在说什么~")],
        }
