from pymongo import MongoClient
from pymongo.server_api import ServerApi
from decouple import config
from config.logger.logger import LOG


PASS = config("ATLASPASS")
NAME = config("ATLASNAME")
ENV = config("ENV")

db_client = MongoClient(
    f"mongodb+srv://{NAME}:{PASS}@{NAME}.dnbgzyq.mongodb.net/?retryWrites=true&w=majority",
    server_api=ServerApi('1'))


def get_db_client():
    if ENV == "development":
        LOG.info("Connected to dev database.")
        return db_client.dev
    elif ENV == "test":
        LOG.info("Connected to test database.")
        return db_client.test
    LOG.info("Connected to prod database.")
    return db_client.prod
