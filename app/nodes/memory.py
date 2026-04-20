# app/nodes/memory.py
from typing import Dict, Any
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.memory_models import MemoryExtraction
from app.prompts.memory_prompts import memory_prompt_template
from app.core.memory_db import get_room_collection, generate_id
from datetime import datetime


def memory_consolidator_node(state: AgentState) -> Dict[str, Any]:
    messages = state.get("messages", [])
    if len(messages) < 2:
        return {}

    # 获取当前用户的标识（如果是 QQ 接入，这里应该是 QQ 号）
    # 在真实流程中，你需要把 user_id 也放进 AgentState 里传递
    user_id = state.get("user_id", "default_user")

    recent_history = f"用户: {messages[-2].content}\n灵犀: {messages[-1].content}"
    print("⏳ [后台] 正在提炼本次对话记忆...")  # 加上这句定位卡点

    # 为了防止大模型在后台整理记忆时超时卡死前端，我们可以设置一个更快的超时或降低 temperature
    llm = get_llm(temperature=0.0).with_config({"request_timeout": 5.0})  # 5秒没提炼完就放弃，别耽误聊天
    structured_llm = llm.with_structured_output(MemoryExtraction)
    chain = memory_prompt_template | structured_llm

    try:
        extraction: MemoryExtraction = chain.invoke({"chat_history": recent_history})

        for item in extraction.extracted_memories:
            if item.importance_score >= 5:
                # 1. 找到对应的记忆房间
                collection = get_room_collection(item.room_category)
                if collection:
                    # 2. 写入 ChromaDB！
                    # documents: 要存的具体内容
                    # metadatas: 元数据，用于过滤。比如这是谁的记忆？哪天存的？
                    # ids: 向量库的唯一主键
                    collection.add(
                        documents=[item.compressed_content],
                        metadatas=[{
                            "user_id": user_id,
                            "importance": item.importance_score,
                            "timestamp": datetime.now().isoformat()
                        }],
                        ids=[f"{user_id}_{generate_id()}"]
                    )
                    print(f"💾 [记忆真实落库] {user_id} -> {item.room_category}: {item.compressed_content}")
            else:
                print("无用的记录")
        return {}  # 写入外部数据库后，不需要再返回给短期 State 了

    except Exception as e:
        print(f"⚠️ 记忆真实入库失败: {e}")
        return {}
