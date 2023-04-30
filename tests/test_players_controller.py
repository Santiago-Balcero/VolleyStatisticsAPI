from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
import pydantic
import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from models.player_models import NewPlayer, NewPassword
from main import app

client = TestClient(app)

player1: NewPlayer = NewPlayer(
    first_name="Calixta",
    last_name="Solar",
    category="Women",
    position="OH",
    email="x@calypsalaloca.com",
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


@pytest.mark.parametrize(
    "first_n, last_n, cat, pos, mail, passw",
    [
        ("", "la Loca", "Women", "OH", "calypsa@laloca.com", "Perritos2023Peludos"),
        ("Calypsa", "", "Women", "OH", "calypsa@laloca.com", "Perritos2023Peludos"),
        ("Calypsa", "la Locaaaaaaaaaaaaaaaaaaaaaaaaa", "Women", "OH", "calypsa@laloca.com",
            "Perritos2023Peludos"),
        ("Calypsa", "la Loca", "en", "OH", "calypsa@laloca.com", "Perritos2023Peludos"),
        ("Calypsa", "la Loca", "Women", "X", "calypsa@laloca.com", "Perritos2023Peludos"),
        ("Calypsa", "la Loca", "Women", "OH", "ca.com", "Perritos2023Peludos"),
        ("Calypsa", "la Loca", "Women", "OH", "calypsa@laloca.com", "rritos202eludos")
    ])
def test_create_player_validation_error(
        first_n: str,
        last_n: str,
        cat: str,
        pos: str,
        mail: str,
        passw: str):
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        player = NewPlayer(
            first_name=first_n,
            last_name=last_n,
            category=cat,
            position=pos,
            email=mail,
            password=passw
        )
        print(player)


@pytest.mark.parametrize(
    "new_pass",
    [
        (""),
        ("password"),
        ("password1289"),
        ("PASAJJSJSL333"),
        ("123456789101112")
    ])   
def test_update_password(new_pass: str):
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        password = NewPassword(new_password=new_pass)
        print(password)
        

def test_get_all_players():
    result = client.get("/players")
    assert result.status_code == 200
    assert type(result.json()) == list
