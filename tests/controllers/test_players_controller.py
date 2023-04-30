from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
import pydantic
import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from models.player_models import NewPlayer
from main import app


client = TestClient(app)

player1: NewPlayer = NewPlayer(
    first_name="Calixta",
    last_name="Solar",
    category="Women",
    position="OH",
    email=pydantic.EmailStr("x@calypsalaloca.com"),
    password="Calypsa2023Pelitos"
)


@pytest.mark.parametrize(
    "player, expected",
    [
        (player1, {"detail": "Player already registered in database."})
    ])
def test_create_player(player: NewPlayer, expected):
    result = client.post("/players", json=jsonable_encoder(player))
    assert result.json() == expected
       

def test_get_all_players():
    result = client.get("/players")
    assert result.status_code == 200
    assert type(result.json()) == list
