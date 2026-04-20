from langchain_core.tools import tool
from datetime import datetime, timedelta


@tool
def get_current_time_tool(days_offset: int = 0) -> str:
    """
    【时间获取工具】
    当你（灵犀）需要知道的时间相关的信息时，必须调用此工具。
    参数 days_offset: 整数。0表示获取今天/现在的时间，1表示获取明天的时间，-1表示获取昨天的时间。
    """
    print(f"🔧 [工具触发] 灵犀看了一眼手表，偏移量: {days_offset}")
    target_date = datetime.now() + timedelta(days=days_offset)
    return target_date.strftime("现在是：%Y年%m月%d日 %H:%M:%S 星期%w (注：星期0代表周日)")
