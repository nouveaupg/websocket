from fastapi import WebSocket
from redis import Redis
import json

from config import logger, connect_to_redis

class ConnectionManager:
    def __init__(self, ws_server_id):
        logger.info("websocket_server_id: %s", ws_server_id)
        self._ws_server_id = ws_server_id
        self._active_connections = {}
        self._redis = connect_to_redis()

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self._redis.set(client_id, self._ws_server_id)
        self._active_connections[client_id] = websocket 
        logger.info("Client connected: %s (server: %s)", client_id, self._ws_server_id)

    def local_clients(self) -> list:
        output = []
        for each in self._active_connections.keys():
            output.append(each)
        return output

    def disconnect(self, websocket: WebSocket):
        found = False
        for key, value in self._active_connections.items():
            if value == websocket:
                del self._active_connections[key]
                logger.info("Client %s disconnected from server. (server: %s)", key, self._ws_server_id)
                found = True
                break
        if not found:
            logger.error("Disconnect: lost connection (server: %s)", self._ws_server_id)

    async def sent_json_to_client(self, client_id: str, object: object):
        if client_id in self._active_connections:
            websocket = self._active_connections[client_id]
            await websocket.send_json(object)
            logger.debug("Message sent to local client %s (server: %s)", client_id, self._ws_server_id)
        else:
            server_id = self._redis.get(client_id)
            self._redis.rpush(server_id, json.dumps(object))
            logger.debug("Client %s not found on this server (server: %s)", client_id, self._ws_server_id)
            logger.debug("Message posted to Redis queue: " + server_id)