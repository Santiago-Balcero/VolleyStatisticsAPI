import pytest
import sys
from decouple import config
from bson import ObjectId
from fastapi.testclient import TestClient

sys.path.append(config("PROJECT_PATH"))

from main import app
from config.db.client import get_db_client

ENV: str = config("ENV")
TEST_TOKEN = config("TEST_TOKEN")
TEST_PLAYER_ID = config("TEST_PLAYER_ID")
TEST_TEAM_ID = config("TEST_TEAM_ID")

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
            get_db_client().players.delete_many(
                {"_id":
                    {"$ne": ObjectId(TEST_PLAYER_ID)}})
            get_db_client().players.update_one(
                {"_id": ObjectId(TEST_PLAYER_ID)},
                {"$pull":
                    {"teams":
                        {"team_id":
                            {"$ne": ObjectId(TEST_TEAM_ID)}}}})
            # This is for keeping total_teams = 1 because only one team is left after DB cleaning
            get_db_client().players.update_one(
                {"_id": ObjectId(TEST_PLAYER_ID)},
                {"$set": {"total_teams": 1}})

    request.addfinalizer(clean_database)


# Some tests will call for this token which is for always existing player in test DB
# Some others may do login with other players as part of the test
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
