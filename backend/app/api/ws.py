from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.websockets.manager import manager
from app.autogen_agents.manager import run_autogen_chat
import json

router = APIRouter(tags=["WebSockets"])

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    # Send welcome message
    await websocket.send_json({
        "sender": "system",
        "message": "Connected to AI Assistant 🟢",
        "timestamp": "now"
    })
    try:
        while True:
            data = await websocket.receive_text()
            
            # Parse message if it's JSON, otherwise treat as string
            try:
                message_data = json.loads(data)
                user_message = message_data.get("message", data)
            except json.JSONDecodeError:
                user_message = data
            
            # Send "typing" status or similar if needed
            # await manager.broadcast({"status": "processing", "sender": "system"})
            
            # Run AutoGen Chat
            try:
                async def send_log(msg):
                    await websocket.send_json(msg)

                response = await run_autogen_chat(user_message, broadcast_callback=send_log)
                
                # Send response back
                await websocket.send_json({
                    "sender": "assistant",
                    "message": response,
                    "timestamp": "now" # In real app use datetime
                })
            except Exception as e:
                print(f"Error in AutoGen chat: {e}")
                await websocket.send_json({
                    "sender": "system",
                    "message": "I'm sorry, I encountered an error processing your request.",
                    "error": str(e)
                })
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
