# app/graph.py 完整版引用
from langgraph.graph import StateGraph, END
from app.core.state import AgentState
from app.nodes.tracker import state_tracker_node
from app.nodes.router import intent_router_edge
from app.nodes.daily_chat import daily_chat_node
from app.nodes.friction import friction_node
from app.nodes.flirt import flirt_node
from app.nodes.empathy import empathy_node
from app.nodes.deep_talk import deep_talk_node
from app.nodes.advice import advice_node
from app.nodes.crisis import crisis_node
from app.nodes.study_node import study_momo_node

from app.nodes.memory import memory_consolidator_node


# (假设你还有一个极简的 breakup_node，如果还没写，可以直接复制 friction 的逻辑稍微改下文本，或者也写成硬编码)
def breakup_node(state: AgentState):
    from langchain_core.messages import AIMessage
    return {"messages": [AIMessage(content="我们之间没什么好说的了。请你以后不要再找我。")], "companion_mood": "心灰意冷"}


# 1. 初始化图网络
workflow = StateGraph(AgentState)

# 2. 注册所有节点
workflow.add_node("tracker", state_tracker_node)
workflow.add_node("daily_chat_node", daily_chat_node)
workflow.add_node("friction_node", friction_node)
workflow.add_node("flirt_node", flirt_node)
workflow.add_node("empathy_node", empathy_node)
workflow.add_node("deep_talk_node", deep_talk_node)
workflow.add_node("advice_node", advice_node)
workflow.add_node("crisis_node", crisis_node)
workflow.add_node("study_momo_node", study_momo_node)
workflow.add_node("breakup_node", breakup_node)
workflow.add_node("memory_consolidator", memory_consolidator_node)
# 3. 定义流转边
workflow.set_entry_point("tracker")
workflow.add_conditional_edges("tracker", intent_router_edge)

# 4. 指向终点
all_leaf_nodes = [
    "daily_chat_node", "friction_node", "flirt_node",
    "empathy_node", "deep_talk_node", "advice_node",
    "crisis_node", "study_momo_node", "breakup_node"
]
for node in all_leaf_nodes:
    # 让所有节点处理完后，都去触发记忆存储
    workflow.add_edge(node, "memory_consolidator")

# 最后，记忆存储完毕，本轮图计算才真正结束
workflow.add_edge("memory_consolidator", END)
# 5. 编译出炉
agent_app = workflow.compile()
