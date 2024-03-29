from pydantic import BaseModel
from logging.config import dictConfig
from redis import Redis
import logging

REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379

def connect_to_redis():
    return Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""

    LOGGER_NAME: str = "websocket"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version = 1
    disable_existing_loggers = False
    formatters = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers = {
        "websocket": {"handlers": ["default"], "level": LOG_LEVEL},
    }

dictConfig(LogConfig().dict())
logger = logging.getLogger("websocket")