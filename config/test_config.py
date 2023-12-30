"""
Module for define config used by app when running tests
"""

import os
import logging
import sys
from mongomock_motor import AsyncMongoMockClient

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://user:aa@localhost:27017/")
MONGODB_ENGINE = AsyncMongoMockClient()
MONGODB_DB = "college"
MONGODB_COLLECTION = "students"
LOG_CONFIG = {
    'name': 'fast-api-webapp-test',
    'level': logging.DEBUG,
    'stream_handler': logging.StreamHandler(sys.stdout),
    'format': '[%(asctime)s] [%(process)s] [%(levelname)s] %(message)s',
    'date_fmt': '%Y-%m-%d %H:%M:%S %z',
}
