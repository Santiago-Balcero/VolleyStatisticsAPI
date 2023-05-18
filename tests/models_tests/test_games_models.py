from fastapi import HTTPException
from fastapi.testclient import TestClient
import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from models.game_models import Game, GameAction, EndGame
from main import app


client = TestClient(app)


@pytest.mark.parametrize(
    "game_co, game_ci, opponent_t, player_num, player_pos",
    [
        ("Col", "Bogotá", "Fener", "99", "MB"),
        ("Colombia", "", "Fener", "99", "MB"),
        ("Colombia", "Bogotá", "", "99", "ANY"),
        ("Colombia", "Bogotá", "Fener", "nueve", "MB"),
        ("Colombia", "Bogotá", "Fener", "99", "XX")
    ])
def test_game_validation_error(
        game_co: str,
        game_ci: str,
        opponent_t: str,
        player_pos: str,
        player_num: str,
        database_clean):
    with pytest.raises(HTTPException):
        game = Game(
            game_country=game_co,
            game_city=game_ci,
            opponent_team=opponent_t,
            player_number=player_num,
            player_position=player_pos)
        print(game)


@pytest.mark.parametrize(
    "team_i, game_i, act, action_res",
    [
        ("644dde8022e3a5c85d0e506b", "644dde8022e3a5c85d0e506b", "att", "point"),
        ("644dde8022e3a5c85d0e506b", "644dde8022e3a5c85d0e506b", "attack", "punt")
    ])
def test_game_action_validation_error(
        team_i: str,
        game_i: str,
        act: str,
        action_res: str):
    with pytest.raises(HTTPException):
        game_action = GameAction(
            team_id=team_i,
            game_id=game_i,
            action=act,
            action_result=action_res)
        print(game_action)


@pytest.mark.parametrize(
    "team_i, game_i",
    [
        ("kjhdas89", "644dde8022e3a5c85d0e506b"),
        ("644dde8022e3a5c85d0e506b", "234656gfgd")
    ])
def test_end_game_validation_error(
        team_i: str,
        game_i: str):
    with pytest.raises(HTTPException):
        game_action = EndGame(
            team_id=team_i,
            game_id=game_i)
        print(game_action)
