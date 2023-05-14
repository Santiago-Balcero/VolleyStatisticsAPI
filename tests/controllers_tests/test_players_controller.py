from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from models.player_models import NewPlayer, PlayerBase, Player, NewPassword
from main import app


client = TestClient(app)

PLAYERS_MAIN_ROUTE = "/players"
LOGIN_ROUTE = "/auth/login"


def test_get_all_players(database_check) -> None:
    result = client.get("/players")
    assert result.status_code == 200
    assert type(result.json()["data"]) == list


player1: NewPlayer = NewPlayer(
    first_name="Calixta",
    last_name="Solar",
    category="Women",
    position="OH",
    email="calypsa@calypsalaloca.com",
    password="Calypsa2023Pelitos"
)

player2: dict = {
    "first_name": "",
    "last_name": "Solar",
    "category": "Women",
    "position": "OH",
    "email": "dasdasdasasdas@calypsalaloca.com",
    "password": "Calypsa2023Pelitos"
}

player3: dict = {
    "first_name": "Calypsa",
    "last_name": "Solar",
    "category": "Women",
    "position": "OH",
    "email": "xa.com",
    "password": "Calypsa2023Pelitos"
}

player4: dict = {
    "first_name": "Calypsa",
    "last_name": "Solar",
    "category": "Women",
    "position": "OH",
    "email": "xa@dasas.com",
    "password": "elitos"
}

player5: NewPlayer = NewPlayer(
    first_name="Calychis",
    last_name="Calychis",
    category="Women",
    position="OH",
    email="loca@loca.com",
    password="Calypsa2023Pelitos"
)

player6: NewPlayer = NewPlayer(
    first_name="Calychis",
    last_name="Calychis",
    category="Women",
    position="OH",
    email="xxx@loca.com",
    password="Calypsa2023Pelitos"
)

updated_player: PlayerBase = PlayerBase(
    first_name="Calypsa",
    last_name="del Perpetuo Socorro",
    category="Women",
    position="L",
    email="zzz@mail.com"
)


@pytest.mark.parametrize(
    "player, expected",
    [
        (player1,
            {"data": None,
                "detail":
                    f"Player {player1.first_name} {player1.last_name} successfully registered."}),
        (player2, {"detail": "Invalid value for first name."}),
        (player3, {"detail": "Invalid value for email."}),
        (player4, {"detail": "Invalid value for password."}),
        (player5,
            {"data": None,
                "detail":
                    f"Player {player5.first_name} {player5.last_name} successfully registered."}),
        (player6,
            {"data": None,
                "detail":
                    f"Player {player6.first_name} {player6.last_name} successfully registered."})
    ])
# This database_clean call is enoguh for the entire test session
def test_create_player(player: NewPlayer, expected: dict, database_clean) -> None:
    result = client.post(PLAYERS_MAIN_ROUTE, json=jsonable_encoder(player))
    assert result.json() == expected
       

def test_get_player_by_id(token_for_tests, database_check) -> None:
    token = token_for_tests
    result = client.get(
        f"{PLAYERS_MAIN_ROUTE}/player",
        headers={"Authorization": f"Bearer {token}"})
    data = result.json()["data"]
    assert type(result.json()) == dict
    assert result.json()["detail"] is None
    assert type(data) == dict
    # Assert data is type Player
    for key in Player.__fields__:
        assert key in data.keys()


@pytest.mark.parametrize(
    "player, new_pass, expected",
    [
        (player1, {"new_password": "abcd123"}, {"detail": "Invalid value for password."}),
        (player1, {"new_password": "Calypsa2023Pelitos"},
            {"data": None, "detail": "Password successfully changed."})
    ]
)
def test_update_password(
    player: NewPlayer,
    new_pass: NewPassword,
    expected: dict,
        database_check):
    result = client.post(
        LOGIN_ROUTE,
        data={
            "username": player.email,
            "password": player.password})
    assert result.json()["access_token"]
    token = result.json()["access_token"]
    result = client.put(
        f"{PLAYERS_MAIN_ROUTE}/password",
        json=jsonable_encoder(new_pass),
        headers={"Authorization": f"Bearer {token}"})
    assert result.json() == expected


def test_update_player(database_check):
    result = client.post(
        LOGIN_ROUTE,
        data={
            "username": player1.email,
            "password": player1.password})
    assert result.json()["access_token"]
    token = result.json()["access_token"]
    result = client.put(
        PLAYERS_MAIN_ROUTE,
        json=jsonable_encoder(updated_player),
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert result.json()["detail"] == "Player successfully updated."
    

def test_delete_player(database_check):
    result = client.post(
        LOGIN_ROUTE,
        data={
            "username": player5.email,
            "password": player5.password})
    assert result.json()["access_token"]
    token = result.json()["access_token"]
    result = client.delete(
        f"{PLAYERS_MAIN_ROUTE}/delete",
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert result.json()["detail"] == "Player successfully deleted."
