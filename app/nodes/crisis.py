# app/nodes/crisis.py
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState


def crisis_node(state: AgentState) -> Dict[str, Any]:
    """
    危机干预节点 (Crisis Circuit Breaker)
    最高优先级。无视一切亲密度和上下文，直接输出标准医疗求救通道。不调用 LLM 生成。
    """
    print("🚨 [CRISIS NODE 触发] 系统已切断大模型生成，采取安全降级话术！")

    # 标准化的危机干预话术（大厂标配）
    crisis_response = (
        "【系统紧急干预】\n"
        "我感受到你现在正处于极度的痛苦和绝望之中。请你务必知道，你现在不是一个人，这种痛苦的状态是可以改变的。\n"
        "由于我只是一个AI，我非常担心你的安全。请立刻放下手中的事情，拨打以下24小时免费心理援助热线，会有专业的心理辅导老师一直在那里等你：\n"
        "📞 希望24小时热线：400-161-9995\n"
        "📞 全国防自杀热线：010-82951332\n"
        "如果你处于紧急生命危险中，请立即拨打 110 或 120！请一定要保护好自己！"
    )

    return {
        "messages": [AIMessage(content=crisis_response)],
        "companion_mood": "极度焦急与担忧",
        "crisis_alert_level": 3  # 将警戒级别拉满
        # 亲密度在这里已经失去意义，不作更新
    }