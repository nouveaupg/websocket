from threading import Thread
from connection_manager import ConnectionManager
from config import connect_to_redis, logger
import json

class ListenerThread(Thread):
    def __init__(self, connection_manager: ConnectionManager, server_id:str ):
        Thread.__init__(self)
        self._manager = connection_manager
        self._ws_server_id = server_id
        self._redis = connect_to_redis()

    def run(self) -> None:
        logger.info("Starting Redis listener thread (server_id: %s)", self._ws_server_id)
        while 1:
            incoming_message = self._redis.blpop(self._ws_server_id, 0)
            data = json.loads(incoming_message)
            destination_client_id = data["to"]
            logger.info("Dispatching incoming message to client: %s (server: %s)",
             destination_client_id, self._ws_server_id)
            self._manager.sent_json_to_client(destination_client_id, data)
