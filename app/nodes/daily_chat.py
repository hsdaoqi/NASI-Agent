from typing import Dict, Any
from langchain_core.messages import AIMessage, ToolMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from app.prompts.chat_prompts import chat_prompt_template
from app.tools.agent_tools import base_tools


def daily_chat_node(state: AgentState) -> Dict[str, Any]:
    """
    日常闲聊节点：使用 Tool Calling 模式，让模型先按需调用工具，再给出结构化回复。
    """
    messages = state.get("messages", [])
    if not messages:
        return {"messages": [AIMessage(content="你先跟我说句话嘛，我在听。")]}

    intimacy = state.get("intimacy_level", 0)
    mood = state.get("companion_mood", "平静")

    llm = get_llm(temperature=0.5).with_config({"request_timeout": 10.0})
    llm_with_tools = llm.bind_tools(base_tools + [CompanionResponse])

    prompt_messages = chat_prompt_template.format_messages(
        intimacy_level=intimacy,
        companion_mood=mood,
        shared_memories=state.get("shared_memories", []),
        chat_history=messages[:-1],
        user_input=messages[-1].content,
    )

    tool_map = {tool.name: tool for tool in base_tools}
    working_messages = list(prompt_messages)
    final_response = None

    try:
        for _ in range(6):
            ai_msg = llm_with_tools.invoke(working_messages)
            working_messages.append(ai_msg)

            tool_calls = ai_msg.tool_calls or []
            if not tool_calls:
                break

            for tool_call in tool_calls:
                name = tool_call.get("name")
                args = tool_call.get("args", {})

                if name == "CompanionResponse":
                    final_response = CompanionResponse(**args)
                    break

                tool = tool_map.get(name)
                if not tool:
                    working_messages.append(
                        ToolMessage(
                            content=f"工具 {name} 不存在，请改用已注册工具。",
                            tool_call_id=tool_call["id"],
                        )
                    )
                    continue

                tool_result = tool.invoke(args)
                working_messages.append(
                    ToolMessage(content=str(tool_result), tool_call_id=tool_call["id"])
                )

            if final_response:
                break

        if not final_response:
            # 兜底：如果模型没走 CompanionResponse 工具，尝试用最后一条文本直出。
            fallback_text = "哎呀我刚刚有点卡住了，你再说一句我认真听。"
            if isinstance(working_messages[-1], AIMessage) and working_messages[-1].content:
                fallback_text = str(working_messages[-1].content)

            return {
                "messages": [AIMessage(content=fallback_text)],
                "companion_mood": mood,
                "intimacy_level": intimacy,
            }

        print(f"💭 [灵犀内心戏]: {final_response.internal_monologue}")
        print(f"💓 [心情转变]: 从 '{mood}' 变成了 '{final_response.new_mood}'")

        new_intimacy = max(-100, min(100, intimacy + final_response.intimacy_delta))
        print(f"📊 [亲密度变化]: {intimacy} -> {new_intimacy}")

        return {
            "messages": [AIMessage(content=final_response.reply_text)],
            "companion_mood": final_response.new_mood,
            "intimacy_level": new_intimacy,
        }

    except Exception as e:
        print(f"⚠️ 生成闲聊回复失败: {e}")
        return {
            "messages": [AIMessage(content="哎呀，我刚刚走神了，没听清你在说什么~")],
        }
