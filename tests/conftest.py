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
TEST_GAME_ID = config("TEST_GAME_ID")

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
            # Deletes all players created during test session
            # Need to keep this document in collection for login tests to work
            get_db_client().players.delete_many(
                {"_id":
                    {"$ne": ObjectId(TEST_PLAYER_ID)}})
            # Deletes all teams created for test player during test session
            get_db_client().players.update_one(
                {"_id": ObjectId(TEST_PLAYER_ID)},
                {"$pull":
                    {"teams":
                        {"team_id":
                            {"$ne": ObjectId(TEST_TEAM_ID)}}}})
            # This is for keeping player total_teams = 1 and total_games = 1
            # because only one team is left after DB cleaning
            # It also resets player statistics
            get_db_client().players.update_one(
                {"_id": ObjectId(TEST_PLAYER_ID)},
                {"$set":
                    {
                        "total_teams": 1,
                        "total_games": 1,
                        "attack_points": 0,
                        "attack_neutrals": 0,
                        "attack_errors": 0,
                        "total_attacks": 0,
                        "attack_effectiveness": 0,
                        "block_points": 0,
                        "block_neutrals": 0,
                        "block_errors": 0,
                        "total_blocks": 0,
                        "block_effectiveness": 0,
                        "service_points": 0,
                        "service_neutrals": 0,
                        "service_errors": 0,
                        "total_services": 0,
                        "service_effectiveness": 0,
                        "defense_perfects": 0,
                        "defense_neutrals": 0,
                        "defense_errors": 0,
                        "total_defenses": 0,
                        "defense_effectiveness": 0,
                        "reception_perfects": 0,
                        "reception_neutrals": 0,
                        "reception_errors": 0,
                        "total_receptions": 0,
                        "reception_effectiveness": 0,
                        "set_perfects": 0,
                        "set_neutrals": 0,
                        "set_errors": 0,
                        "total_sets": 0,
                        "set_effectiveness": 0,
                        "total_points": 0,
                        "total_perfects": 0,
                        "total_neutrals": 0,
                        "total_errors": 0,
                        "total_actions": 0,
                        "total_effectiveness": 0}})
            # Deletes all games created for test player/team during test session
            get_db_client().players.update_one(
                {"teams": {"$elemMatch": {"team_id": ObjectId(TEST_TEAM_ID)}}},
                {"$pull":
                    {"teams.$.games":
                        {"game_id":
                            {"$ne": ObjectId(TEST_GAME_ID)}}}})
            # This is for keeping team total_games = 1
            # because only one game is left after DB cleaning
            get_db_client().players.update_one(
                {"teams": {"$elemMatch": {"team_id": ObjectId(TEST_TEAM_ID)}}},
                {"$set": {"teams.$.total_games": 1}})
            # This is for test game to remain active after DB cleaning
            get_db_client().players.update_one(
                {"teams.games.game_id": ObjectId(TEST_GAME_ID)},
                {"$set": {"teams.$[t].games.$[g].status": 1}},
                array_filters=[
                    {"t.team_id": ObjectId(TEST_TEAM_ID)},
                    {"g.game_id": ObjectId(TEST_GAME_ID)}])
            # TODO clean all test player/team/game statistics, set them to 0

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
