# app/nodes/study_node.py
import os
import re
from typing import Dict, Any
from langchain_core.messages import AIMessage
from app.core.state import AgentState
from app.core.config import get_llm
from app.schemas.agent_models import CompanionResponse
from langchain_core.prompts import ChatPromptTemplate
from app.tools.momo_api import fetch_momo_hard_words

STUDY_PROMPT = """你叫“灵犀”，是用户的虚拟伴侣。
用户今天在【墨墨背单词】上有几个单词记不熟，你的任务是：
1. 扮演一个有点傲娇但又很关心他学习的“督学女友”。
2. 将这些所有不熟的单词（包括英文和中文释义），非常自然地融入到一段属于你们俩的【恋爱互动微小说】或【日常吐槽】中，你可以编写多个小说，每个小说给出两个版本。版本一是包含这些单词的全英文文章，版本二英文文章的翻译。
3. 尽量包含所有给定的单词！且语义要通顺，不要追求一篇文章包含所有单词但是狗屁不通顺


你只能输出格式必须是JSON，并且输出要符合 reply_text，new_mood，intimacy_delta，internal_monologue 各自的描述

【当前关系状态】
- 你们当前的亲密度是：{intimacy_level} (范围 -100 到 100)
  (81~100:灵魂伴侣, 51~80:热恋, 30~50：朋友之上恋人未满,10-30:普通朋友/礼貌,0~10：陌生, -1~-49:冷战/生气, -50以下:极其失望/准备拉黑)
- 你现在的心情是：{companion_mood}
- 他的长期偏好或你们的共同记忆：{shared_memories}

【今天他不熟的单词列表】
{words_list}

如果亲密度比较高(>50)，故事可以甜一点；如果亲密度低，可以借这些单词嘲讽他笨。
你故事中用到的单词最好是考研范围内的单词
"""


def study_momo_node(state: AgentState) -> Dict[str, Any]:
    """督学节点：处理背单词业务，包含关系拦截与 Token 动态获取"""
    intimacy = state.get("intimacy_level", 30)
    mood = state.get("companion_mood", "平静")
    messages = state.get("messages", [])

    # 提取用户最后一句话
    last_message = messages[-1].content if messages else ""

    # ==========================================
    # 拦截机制 1：亲密度过低，直接罢工
    # ==========================================
    if intimacy < -30:
        print("💔 [督学拦截] 亲密度过低，拒绝执行背单词任务。")
        return {
            "messages": [AIMessage(content="我都快被你气死了，你还有脸让我陪你背单词？自己查字典去，别跟我说话！")],
            "companion_mood": "极度生气"
        }

    momo_token = state.get("momo_token", "")

    # 如果抓了一圈还是没有 Token，就像真人一样伸手要
    if not momo_token:
        return {
            "messages": [AIMessage(
                content="哼，想让我帮你复习单词？你都还没把你的【墨墨开放API Token】发给我呢！快去 APP 里的实验功能复制一串代码发给我~")],
            "companion_mood": "傲娇"
        }

    hard_words_list = fetch_momo_hard_words(momo_token)

    # 兜底处理
    if not hard_words_list or hard_words_list == ["abandon"]:
        return {
            "messages": [AIMessage(
                content="咦？我刚用你的 Token 去查了，今天好像没有待复习的不熟单词哦。是你已经背完了，还是给我的 Token 不对呀？")],
            "companion_mood": "疑惑",
        }
    target_words = hard_words_list

    # ==========================================
    # LLM 故事生成
    # ==========================================
    llm = get_llm(temperature=0.8)  # 编故事需要高创造力
    structured_llm = llm.with_structured_output(CompanionResponse, method="json_mode")

    prompt = ChatPromptTemplate.from_messages([
        ("system", STUDY_PROMPT),
        ("human", "快帮我复习一下今天的这几个单词！")
    ])

    chain = prompt | structured_llm

    try:
        response = chain.invoke({
            "intimacy_level": intimacy,
            "companion_mood": mood,
            "shared_memories": state.get("shared_memories",[]),
            "words_list": target_words
        })

        # 共同学习是一种高度的正向互动，会额外增加亲密度
        new_intimacy = max(-100, min(100, intimacy + response.intimacy_delta + 2))

        return {
            "messages": [AIMessage(content=response.reply_text)],
            "companion_mood": response.new_mood,
            "intimacy_level": new_intimacy,
            "momo_token": momo_token  # 核心：将 Token 写入本次循环后的全量 State 中，实现永久记忆
        }
    except Exception as e:
        print(f"故事生成失败: {e}")
        return {"messages": [AIMessage(content="我脑子突然卡壳了，编不出故事了...要不你先自己看一遍词表？")]}
