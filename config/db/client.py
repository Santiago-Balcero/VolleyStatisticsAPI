from pymongo import MongoClient
from decouple import config

PASS = config("ATLASPASS")

dbClient = MongoClient(f"mongodb+srv://volleystatistics:{PASS}@volleystatistics.dnbgzyq.mongodb.net/?retryWrites=true&w=majority").test
