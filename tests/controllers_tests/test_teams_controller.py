from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
import sys
import pytest
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from main import app
from models.team_models import Team, UpdatedTeam

TEST_TEAM_ID = config("TEST_TEAM_ID")

client = TestClient(app)

TEAMS_MAIN_ROUTE = "/teams"


def test_get_all_teams(database_check):
    result = client.get(TEAMS_MAIN_ROUTE)
    assert result.status_code == 200
    assert type(result.json()["data"]) == list


def test_get_teams_by_player(token_for_tests, database_check):
    token = token_for_tests
    result = client.get(
        f"{TEAMS_MAIN_ROUTE}/player",
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert type(result.json()["data"]) == list


def test_get_team_by_id(token_for_tests, database_check):
    token = token_for_tests
    result = client.get(
        f"{TEAMS_MAIN_ROUTE}/{TEST_TEAM_ID}",
        headers={"Authorization": f"Bearer {token}"})
    data = result.json()["data"]
    assert type(result.json()) == dict
    assert result.json()["detail"] is None
    assert type(data) == dict
    # Assert data is type Player
    for key in Team.__fields__:
        assert key in data.keys()


team1: Team = Team(
    team_name="Perritos",
    team_category="Mixed"
)

team2: Team = Team(
    team_name="Vakif",
    team_category="Men"
)

team3: Team = Team(
    team_name="Brasil",
    team_category="Women"
)

# Teams 3 and 4 are dicts to make it possible to send them as input and test endpoint
# If they were Team validation error will raise
team4: dict = {
    "team_name": "",
    "team_category": "Mixed"
}

team5: dict = {
    "team_name": "Dynavit",
    "team_category": "x"
}


def test_good_create_team(token_for_tests, database_check):
    token = token_for_tests
    result = client.post(
        f"{TEAMS_MAIN_ROUTE}/new_team",
        json=jsonable_encoder(team1),
        headers={"Authorization": f"Bearer {token}"})
    data = result.json()["data"]
    assert type(result.json()) == dict
    assert result.json()["detail"] == f"Team {team1.team_name} successfully registered."
    assert result.json()["data"]
    # Assert data is type Player
    for key in Team.__fields__:
        assert key in data.keys()


@pytest.mark.parametrize(
    "new_t, expected",
    [
        (team2, {"detail": "Team already registered in player's database."}),
        (team4, {"detail": "Invalid value for team name."}),
        (team5, {"detail": "Invalid value for team category."})
    ]
)
def test_wrong_create_team(new_t: Team, expected: dict, token_for_tests, database_check):
    token = token_for_tests
    result = client.post(
        f"{TEAMS_MAIN_ROUTE}/new_team",
        json=jsonable_encoder(new_t),
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert result.json() == expected


@pytest.mark.parametrize(
    "new_team_n, expected",
    [
        ({"team_id": TEST_TEAM_ID, "new_team_name": "Dynavit"},
            {"data": None, "detail": "Team changed it's name to Dynavit."}),
        ({"team_id": TEST_TEAM_ID, "new_team_name": "Vakif"},
            {"data": None, "detail": "Team changed it's name to Vakif."})
    ]
)
def test_update_team_name(new_team_n: UpdatedTeam, expected: dict, token_for_tests, database_check):
    token = token_for_tests
    result = client.put(
        TEAMS_MAIN_ROUTE,
        json=jsonable_encoder(new_team_n),
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert result.json() == expected


def test_delete_team(token_for_tests, database_check):
    token = token_for_tests
    result = client.post(
        f"{TEAMS_MAIN_ROUTE}/new_team",
        json=jsonable_encoder(team3),
        headers={"Authorization": f"Bearer {token}"})
    data = result.json()["data"]
    assert type(result.json()) == dict
    assert result.json()["detail"] == f"Team {team3.team_name} successfully registered."
    assert result.json()["data"]
    # Assert data is type Player
    for key in Team.__fields__:
        assert key in data.keys()
    team_id = data["team_id"]
    result = client.delete(
        f"{TEAMS_MAIN_ROUTE}/{team_id}",
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert result.json()["detail"] == "Team successfully deleted."
    