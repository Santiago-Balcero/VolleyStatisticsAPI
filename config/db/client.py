from pymongo import MongoClient
from pymongo.server_api import ServerApi
from decouple import config


PASS = config("ATLASPASS")
NAME = config("ATLASNAME")
ENV = config("ENV")

db_client = MongoClient(
    f"mongodb+srv://{NAME}:{PASS}@{NAME}.dnbgzyq.mongodb.net/?retryWrites=true&w=majority",
    server_api=ServerApi('1'))


def get_db_client():
    if ENV == "development":
        return db_client.dev
    elif ENV == "test":
        return db_client.test
    return db_client.prod
