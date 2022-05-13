from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from uuid import uuid4
from connection_manager import ConnectionManager
import uvicorn

app = FastAPI()

ws_server_id = str(uuid4())

manager = ConnectionManager(ws_server_id)

@app.websocket('/ws/{client_uuid}')
async def websocket_endpoint(websocket: WebSocket, client_uuid: str):
    await manager.connect(websocket, client_uuid)
    await websocket.send_json({"connected_clients": manager.local_clients()})
    try:
        while True:
            data = await websocket.receive_json()
            destination_client_uuid = data["to"]
            await manager.sent_json_to_client(destination_client_uuid, data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)