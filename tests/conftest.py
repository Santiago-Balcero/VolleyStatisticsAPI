import pytest
import sys
from decouple import config
from bson import ObjectId
from fastapi.testclient import TestClient

sys.path.append(config("PROJECT_PATH"))

from main import app
from config.db.client import get_db_client
from routers.login_controller import login

ENV: str = config("ENV")
TEST_TOKEN = config("TEST_TOKEN")

client = TestClient(app)


@pytest.fixture(scope="session")
def database_clean(request):
    # Stops tests execution if ENV != "test" to avoid affecting dev or prod databases
    # DO NOT CHANGE
    if ENV != "test":
        pytest.exit("No connection with test database.")

    # Must set ENV in .env to "test"
    def clean_database():
        if ENV == "test":
            # Need to keep this document in collection for login tests to work
            get_db_client().players.delete_many({"_id":
                {"$ne": ObjectId("645bd832512f5603aac42e59")}})
    
    request.addfinalizer(clean_database)
    

@pytest.fixture(scope="session")
def token_for_tests():
    # Stops tests execution if ENV != "test" to avoid affecting dev or prod databases
    # DO NOT CHANGE
    if ENV != "test":
        pytest.exit("No connection with test database.")
    return TEST_TOKEN

@pytest.fixture(scope="session")
def database_check():
    # Stops tests execution if ENV != "test" to avoid affecting dev or prod databases
    # DO NOT CHANGE
    if ENV != "test":
        pytest.exit("No connection with test database.")
