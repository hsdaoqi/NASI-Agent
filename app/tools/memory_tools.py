# app/tools/memory_tools.py
from langchain_core.tools import tool
from app.core.memory_db import room_preferences, room_romance_diary, room_study_progress


@tool
def search_memory_tool(query: str, category: str = "all") -> str:
    """
    【记忆检索工具】
    当你（灵犀）需要回忆用户的过去经历、偏好、习惯或你们的恋爱日记时，必须调用此工具。
    参数 query: 你提炼的精准搜索关键词（例如："不喜欢吃什么", "考研复试时间"）
    参数 category: 指定搜索的房间，可选值："preferences", "romance_diary", "study_progress", "all"
    """
    print(f"🔧 [Agent工具调用] 正在使用 search_memory_tool 搜索: '{query}'")

    # 这里写我们之前的 ChromaDB 搜索逻辑
    results = []
    # 为了简化，假设如果是 all 就全查一遍
    # ... (真实的 chroma_db.query 代码) ...

    return "检索到的记忆: [明日考研复试]"  # 模拟返回结果


@tool
def save_memory_tool(content: str, category: str, importance: int) -> str:
    """
    【记忆存储工具】
    当用户告诉你重要的个人信息（如生日、忌口），或者你们发生了重要情感事件（如大吵一架、表白）时，调用此工具将其永久保存。
    参数 content: 高度压缩的记忆内容（如 "不喜欢吃香菜"）
    参数 category: "preferences", "romance_diary", "study_progress"
    参数 importance: 重要程度 1-10
    """
    print(f"🔧 [Agent工具调用] 正在使用 save_memory_tool 保存: '{content}'")
    # ... (真实的 chroma_db.add 代码) ...
    return "记忆保存成功"
