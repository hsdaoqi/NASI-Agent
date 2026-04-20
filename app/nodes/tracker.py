import re
from typing import Dict, Any

from app.core.memory_db import room_romance_diary, room_preferences, room_study_progress
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import IntentClassification  # 假设已包含新增的 apology 等意图
from app.prompts.router_prompts import router_prompt_template


def state_tracker_node(state: AgentState) -> Dict[str, Any]:
    """
    状态追踪节点：每次用户发言后，第一步必定经过这里。
    它不负责回复，只负责极其敏锐地“读空气”，更新用户的当前状态。
    """
    messages = state.get("messages", [])
    if not messages:
        return {}

    last_message = messages[-1].content
    chat_history = [f"{m.type}: {m.content}" for m in messages[:-1]]
    user_id = state.get("user_id", "default_user")
    intimacy_level = state.get("intimacy_level", 30)
    companion_mood = state.get("companion_mood", "平静")

    # ==========================================
    # 🛡️ 核心新增：数据脱敏层 (Data Masking)
    # ==========================================
    safe_last_message = last_message
    extracted_token = state.get("momo_token", "")  # 继承之前可能存在的 Token

    # 如果用户的话里包含极长字符串，认定为 Token
    token_match = re.search(r'[a-zA-Z0-9\-_]{64}', last_message)
    if token_match:
        extracted_token = token_match.group(0)
        # 把大模型能看到的那句话，强行替换掉
        safe_last_message = last_message.replace(extracted_token, "[API_TOKEN_PROVIDED]")
        print(f"🛡️ [Tracker防线] 成功拦截敏感 Token，已对大模型视野进行屏蔽！")

    retrieved_memories = []
    try:
        # 去恋爱日记本里找找，有没有和当前这句话相关的回忆？
        # where={"user_id": user_id} 确保绝对不会看到别人的记忆！
        diary_results = room_romance_diary.query(
            query_texts=[safe_last_message],
            n_results=3,  # 取最相关的 2 条
            where={"user_id": user_id}
        )
        if diary_results and diary_results['documents'][0]:
            retrieved_memories.extend(diary_results['documents'][0])

        # 同理，去偏好档案室里找找
        pref_results = room_preferences.query(
            query_texts=[safe_last_message],
            n_results=3,
            where={"user_id": user_id}
        )
        if pref_results and pref_results['documents'][0]:
            retrieved_memories.extend(pref_results['documents'][0])
        study_results = room_study_progress.query(
            query_texts=[safe_last_message],
            n_results=3,
            where={"user_id": user_id}
        )
        if study_results and study_results['documents'][0]:
            retrieved_memories.extend(study_results['documents'][0])
        print(f"📖 [记忆唤醒] 匹配到 {len(retrieved_memories)} 条过去的回忆: {retrieved_memories}")
    except Exception as e:
        print(f"⚠️ 记忆读取失败 (可能库还是空的): {e}")

    # ==========================================
    # 意图识别
    # ==========================================
    llm = get_llm(temperature=0.0)
    structured_llm = llm.with_structured_output(IntentClassification)
    chain = router_prompt_template | structured_llm
    try:
        # 注意这里！传给 LLM 的 user_input 是 safe_last_message！
        analysis_result = chain.invoke({
            "chat_history": chat_history,
            "intimacy_level": intimacy_level,
            "companion_mood": companion_mood,
            "user_input": safe_last_message
        })

        print(f"👁️ [灵犀在观察] 意图: {analysis_result.intent}, 强度: {analysis_result.emotion_intensity}")
        print(f"🧠 [灵犀的判断理由]: {analysis_result.reasoning}")

        crisis_level = 2 if analysis_result.intent == "crisis" else 0

        # 返回更新字典
        return {
            "detected_intent": analysis_result.intent,
            "user_emotion": analysis_result.user_emotion,
            "emotion_intensity": analysis_result.emotion_intensity,
            "crisis_alert_level": crisis_level,
            "momo_token": extracted_token,  # 【第一关就把它存进全局 State，后面谁想用谁去取】
            # 【重要】把唤醒的长期记忆塞回 State，这样下游的节点（比如深度交心、日常聊天）就能看见了！
            "shared_memories": retrieved_memories
        }
    except Exception as e:
        print(f"⚠️ 状态嗅探失败: {e}")
        return {"detected_intent": "daily_chat", "shared_memories": []}
