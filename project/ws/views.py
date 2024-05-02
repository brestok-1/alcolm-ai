from fastapi import WebSocket, WebSocketDisconnect
from . import ws_router
from ..bot.chatbot import ChatBot


@ws_router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    chatbot = ChatBot()
    try:
        while True:
            data = await websocket.receive_json()
            async for chunk in chatbot.ask(data['query']):
                await websocket.send_text(chunk)
    except WebSocketDisconnect:
        pass
