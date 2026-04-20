from typing import Literal
from app.core.state import AgentState


def intent_router_edge(state: AgentState) -> str:
    """
    条件路由边：根据 tracker 更新好的状态，决定下一步把任务抛给哪个子节点。
    这里的 if/else 顺序极其关键，代表了处理的优先级。
    """
    intimacy = state.get("intimacy_level", 30)
    intent = state.get("detected_intent", "daily_chat")

    # 🔴 优先级 1：生命危险 (无视一切，立刻抢救)
    if state.get("crisis_alert_level", 0) >= 2 or intent == "crisis":
        print("🚨 触发红色警报，进入 crisis_node")
        return "crisis_node"

    # ⚫ 优先级 2：情感破产 / 决裂 (Game Over)
    # 如果亲密度跌破 -50，或者用户做了极度恶劣的事 (angry)
    if intimacy <= -50 or intent == "angry":
        print("💔 情感彻底破裂，触发 breakup_node (拉黑/决裂)")
        return "breakup_node"

    # 🔵 优先级 3：冷战拦截期 (亲密度为负，只能摩擦或道歉)
    if intimacy < 0:
        if intent == "apology":
            print("🌧️ 对方开始道歉，导向 friction_node 进行考核")
            return "friction_node"
        else:
            print("❄️ 冷战期拒绝正常交流，强制拦截至 friction_node")
            return "friction_node"

    # 🟢 优先级 4：正向恋爱推拉 (亲密度 >= 0)
    if intent == "relationship_friction":
        return "friction_node"  # 日常小吵小闹/吃醋
    elif intent == "flirt_tease":
        return "flirt_node"  # 调情拉扯
    elif intent == "emo_support":
        return "empathy_node"  # 情绪抚慰
    elif intent == "deep_talk":
        return "deep_talk_node"  # 深度交心
    elif intent == "life_planner":
        return "advice_node"  # 给建议
    elif intent == "study_momo":
        return "study_momo"
    # ⚪ 兜底逻辑：日常闲聊
    return "daily_chat_node"
