from fastapi.testclient import TestClient
from fastapi.encoders import jsonable_encoder
import sys
import pytest
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from main import app
from models.team_models import Team
from models.game_models import Game, EndGame, GameAction

TEST_GAME_ID = config("TEST_GAME_ID")
TEST_TEAM_ID = config("TEST_TEAM_ID")

client = TestClient(app)

GAMES_MAIN_ROUTE = "/games"
TEAMS_MAIN_ROUTE = "/teams"


def test_get_game_by_id(token_for_tests, database_clean, database_check):
    token = token_for_tests
    result = client.get(
        f"{GAMES_MAIN_ROUTE}/{TEST_GAME_ID}",
        headers={"Authorization": f"Bearer {token}"})
    data = result.json()["data"]
    assert type(result.json()) == dict
    assert type(result.json()["data"]) == dict
    # Assert data is type Game
    for key in Game.__fields__:
        assert key in data.keys()
        

@pytest.mark.parametrize(
    "game_i, expected",
    [
        ("646575c9ecda2d0a13333de", {"detail": "Invalid value for game id."}),
        ("646575c9ecda2d0a13333de9", {"detail": "Game not found."})
    ]
)
def test_get_game_by_id_exceptions(game_i: str, expected: dict, token_for_tests, database_check):
    token = token_for_tests
    result = client.get(
        f"{GAMES_MAIN_ROUTE}/{game_i}",
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert type(result.json()["detail"]) == str
    assert result.json() == expected


end_game1: EndGame = EndGame(
    team_id=TEST_TEAM_ID,
    game_id=TEST_GAME_ID
)


@pytest.mark.parametrize(
    "end_ga, expected",
    [
        (end_game1, {"data": None, "detail": f"Game with id {TEST_GAME_ID} was finished."}),
        (end_game1, {"detail": "Game was already finished."})
    ]
)
def test_finish_game(end_ga: EndGame, expected: dict, token_for_tests, database_check):
    token = token_for_tests
    result = client.put(
        f"{GAMES_MAIN_ROUTE}/finish_game",
        json=jsonable_encoder(end_ga),
        headers={"Authorization": f"Bearer {token}"})
    assert type(result.json()) == dict
    assert type(result.json()["detail"]) == str
    assert result.json() == expected
    

game1: Game = Game(
    game_country="Colombia",
    game_city="Bogotá",
    opponent_team="Brasil",
    player_position="MB",
    player_number="99"
)


def test_create_game(token_for_tests, database_check):
    token = token_for_tests
    result = client.post(
        f"{GAMES_MAIN_ROUTE}/{TEST_TEAM_ID}",
        json=jsonable_encoder(game1),
        headers={"Authorization": f"Bearer {token}"})
    game = result.json()["data"]
    game_id = game["game_id"]
    assert type(result.json()) == dict
    assert result.json()["detail"] == f"Game {game_id} has started."
    # Assert data type is Game
    for key in Game.__fields__:
        assert key in game.keys()
    result = client.put(
        f"{GAMES_MAIN_ROUTE}/finish_game",
        json=jsonable_encoder({
            "team_id": TEST_TEAM_ID,
            "game_id": game_id
        }),
        headers={"Authorization": f"Bearer {token}"})
    assert result.json()["detail"] == f"Game with id {game_id} was finished."


game2: Game = Game(
    game_country="Colombia",
    game_city="Bogotá",
    opponent_team="UPN",
    player_position="MB",
    player_number="99"
)


team1: Team = Team(
    team_name="Praia",
    team_category="Women"
)


def test_play_game(token_for_tests, database_check):
    token = token_for_tests
    # Creates new team for test
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
    team_id = data["team_id"]
    # Creates new game for test
    result = client.post(
        f"{GAMES_MAIN_ROUTE}/{team_id}",
        json=jsonable_encoder(game2),
        headers={"Authorization": f"Bearer {token}"})
    game = result.json()["data"]
    game_id = game["game_id"]
    assert type(result.json()) == dict
    assert result.json()["detail"] == f"Game {game_id} has started."
    # Assert data type is Game
    for key in Game.__fields__:
        assert key in game.keys()
    # Define game actions and results for different scenarios
    # Invalid team_id
    game_action1: dict = {
        "team_id": "644dde8822e3a5c",
        "game_id": game_id,
        "action": "attack",
        "action_result": "point"
    }
    game_action1_result: dict = {
        "detail": "Invalid value for team id."
    }
    # Team not found
    game_action2: dict = {
        "team_id": "644dde8822e3a5c85d0e506c",
        "game_id": game_id,
        "action": "attack",
        "action_result": "point"
    }
    game_action2_result: dict = {
        "detail": "Team not found."
    }
    # Invalid game_id
    game_action3: dict = {
        "team_id": team_id,
        "game_id": "644dde8822e3a5c85d0",
        "action": "attack",
        "action_result": "point"
    }
    game_action3_result: dict = {
        "detail": "Invalid value for game id."
    }
    # Game not found
    game_action4: dict = {
        "team_id": team_id,
        "game_id": "644dde8822e3a5c85d0e506c",
        "action": "attack",
        "action_result": "point"
    }
    game_action4_result: dict = {
        "detail": "Game not found."
    }
    # Invalid action
    game_action5: dict = {
        "team_id": team_id,
        "game_id": game_id,
        "action": "atta",
        "action_result": "point"
    }
    game_action5_result: dict = {
        "detail": "Invalid value for action."
    }
    # Invalid action_result
    game_action6: dict = {
        "team_id": team_id,
        "game_id": game_id,
        "action": "attack",
        "action_result": "poi"
    }
    game_action6_result: dict = {
        "detail": "Invalid value for action result."
    }
    # Invalid action and action_result combination
    game_action7: dict = {
        "team_id": team_id,
        "game_id": game_id,
        "action": "attack",
        "action_result": "perfect"
    }
    game_action7_result: dict = {
        "detail": "Invalid combination for action and action result."
    }
    # Valid for play game
    game_action8: GameAction = GameAction(
        team_id=team_id,
        game_id=game_id,
        action="attack",
        action_result="point"
    )
    game_action9: GameAction = GameAction(
        team_id=team_id,
        game_id=game_id,
        action="block",
        action_result="point"
    )
    game_action10: GameAction = GameAction(
        team_id=team_id,
        game_id=game_id,
        action="defense",
        action_result="perfect"
    )
    actions: list = [
        game_action1,
        game_action2,
        game_action3,
        game_action4,
        game_action5,
        game_action6,
        game_action7,
        game_action8,
        game_action9,
        game_action10
    ]
    results: list = [
        game_action1_result,
        game_action2_result,
        game_action3_result,
        game_action4_result,
        game_action5_result,
        game_action6_result,
        game_action7_result
    ]
    # Play game
    for i in range(len(actions)):
        result = client.put(
            f"{GAMES_MAIN_ROUTE}/play_game",
            json=jsonable_encoder(actions[i]),
            headers={"Authorization": f"Bearer {token}"})
        assert type(result.json()) == dict
        if i < 7:
            assert result.json() == results[i]
        else:
            for key in Game.__fields__:
                assert key in result.json()["data"].keys()
