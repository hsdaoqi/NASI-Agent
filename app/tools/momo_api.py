# app/tools/momo_api.py
import requests
import os
from typing import List, Dict


def fetch_momo_hard_words(token: str) -> List[str]:
    """
    调用墨墨背单词开放 API，获取标记为"模糊"和"忘记"的不熟单词。
    （注：目前官方接口刚开放，此处为标准 RESTful API 模拟结构，
    实际开发时请替换为你在 APP 里看到的真实 URL）
    """
    if not token:
        return ["abandon"]  # 兜底假数据
    # 接口配置
    url = "https://open.maimemo.com/open/api/v1/study/get_today_items"
    payload = {
        "is_finished": True,
        "is_new": False,
        "limit": 300  # 拉取今日最多1000个待学单词（接口上限）
    }
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()  # 自动抛出HTTP错误（如401/403/500）

        # 4. 解析并过滤数据
        data = response.json().get("data", {})
        all_records = data.get("today_items", [])
        if not all_records:
            return ["abandon"]
        is_no_familary = [record["voc_spelling"] for record in all_records]
        return is_no_familary
    except Exception as e:
        print(f"获取墨墨数据失败: {e}")
        return ["abandon"]
