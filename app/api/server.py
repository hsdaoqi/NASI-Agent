# server.py (或 app/api/server.py)
import json
import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage
from app.graph import agent_app

app = FastAPI(title="LingXi Companion API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模拟一个内存数据库，存储会话状态（真实项目应存在 Redis 或 Postgres）
session_db = {}


@app.websocket("/ws/chat/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()

    # 初始化用户的会话状态
    if session_id not in session_db:
        session_db[session_id] = {
            "messages": [],
            "intimacy_level": 0,  # 初始亲密度
            "companion_mood": "平静"
        }

    try:
        while True:
            # 1. 接收前端发来的文字
            user_text = await websocket.receive_text()
            print(f"收到用户 {session_id} 的消息: {user_text}")

            # 2. 组装输入状态
            input_state = session_db[session_id]
            input_state["messages"].append(HumanMessage(content=user_text))

            # 发送状态：思考中
            await websocket.send_json({"type": "status", "content": "灵犀正在思考..."})

            # 3. 执行 LangGraph 图网络 (这里用 ainvoke 简化演示，生产环境可用 astream 获取流式 token)
            # 配置 thread_id 保证记忆追踪
            config = {"configurable": {"thread_id": session_id}}
            final_state = await agent_app.ainvoke(input_state, config=config)

            # 4. 更新内存状态
            session_db[session_id] = final_state

            # 5. 提取最新的 AI 回复、亲密度和心情
            ai_reply = final_state["messages"][-1].content
            current_mood = final_state.get("companion_mood")
            current_intimacy = final_state.get("intimacy_level")

            # 6. 把全套状态推送给前端
            await websocket.send_json({
                "type": "message",
                "content": ai_reply,
                "mood": current_mood,
                "intimacy": current_intimacy
            })

    except WebSocketDisconnect:
        print(f"用户 {session_id} 断开连接")
    except Exception as e:
        print(f"服务器错误: {e}")
        await websocket.send_json({"type": "error", "content": "服务器开小差了~"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
