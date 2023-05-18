from fastapi import HTTPException
import pydantic
import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from models.player_models import NewPlayer, NewPassword


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
def test_new_player_validation_error(
        first_n: str,
        last_n: str,
        cat: str,
        pos: str,
        mail: pydantic.EmailStr,
        passw: str,
        database_clean):
    with pytest.raises(HTTPException):
        player = NewPlayer(
            first_name=first_n,
            last_name=last_n,
            category=cat,
            position=pos,
            email=mail,
            password=passw)
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
    with pytest.raises(HTTPException):
        password = NewPassword(new_password=new_pass)
        print(password)
