from pymongo import MongoClient
from pymongo.server_api import ServerApi
from decouple import config

PASS = config("ATLASPASS")
NAME = config("ATLASNAME")
ENV = config("ENV")

test_db_client = MongoClient(
    f"mongodb+srv://{NAME}:{PASS}@{NAME}.dnbgzyq.mongodb.net/?retryWrites=true&w=majority",
    server_api=ServerApi('1')).test

prod_db_client = MongoClient(
    f"mongodb+srv://{NAME}:{PASS}@{NAME}.dnbgzyq.mongodb.net/?retryWrites=true&w=majority",
    server_api=ServerApi('1')).prod


def get_db_client():
    if ENV == "development":
        return test_db_client
    return prod_db_client
