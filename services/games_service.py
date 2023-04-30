from bson import ObjectId
from pymongo import ReturnDocument
from models.game_models import EndGame, Game, GameAction
from models.team_models import Team
from schemas.game_schemas import game_from_player
from schemas.team_schemas import teams_from_player
import services.teams_service as TeamService
from config.db.client import get_db_client
from config.logger.logger import LOG
from utils.constants import GAME_ACTIONS
from utils import exceptions as ex


def get_game_by_id(game_id: str) -> Game:
    if not ObjectId.is_valid(game_id):
        ex.invalid_object_id("game")
    try:
        game: Game = game_from_player(get_db_client().players.find_one(
            {"teams.games.game_id": ObjectId(game_id)},
            {"teams.games": 1}),
            game_id)
    except Exception as exception:
        ex.no_data_connection("gamesService/get_game_by_id/find_one", exception)
    if game is None:
        ex.game_not_found()
    return game


def create_game(team_id: str, new_game: Game, player_id: str) -> bool:
    try:
        teams: list[Team] = teams_from_player(get_db_client().players.find_one(
            {"teams.team_id": ObjectId(team_id)}, 
            {"teams": 1}))
    except Exception as exception:
        ex.no_data_connection("teamsService/create_game/find_one", exception)
    if teams is None:
        ex.team_not_found()
    TeamService.check_for_existing_team(team_id)
    # Can´t begin a new match if there are others that have not finished yet
    check_for_active_games(teams)
    new_game.game_id = ObjectId()
    while not validate_game_id(new_game.game_id):
        LOG.debug("Repeated game_id in DB, trying again with new value.")
        new_game.game_id = ObjectId()
    game_dict: dict = dict(new_game)
    try:
        result = get_db_client().players.update_one(
            {"teams": {"$elemMatch": {"team_id": ObjectId(team_id)}}},
            {"$push": {"teams.$.games": game_dict}})
    except Exception as exception:
        ex.no_data_connection("teamsService/create_game/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_create_game()
    TeamService.sum_team_games(team_id, player_id)
    return True


def finish_game(game_to_finish: EndGame) -> bool:
    TeamService.check_for_existing_team(game_to_finish.team_id)
    check_for_existing_game(game_to_finish.game_id)
    try:
        result = get_db_client().players.update_one(
            {"teams.games.game_id": ObjectId(game_to_finish.game_id)},
            {"$set": {"teams.$[t].games.$[g].status": 0}},
            array_filters=[
                {"t.team_id": ObjectId(game_to_finish.team_id)},
                {"g.game_id": ObjectId(game_to_finish.game_id)}])
    except Exception as exception:
        ex.no_data_connection("teamsService/finish_game/update_one", exception)
    if result.modified_count != 1:
        ex.game_already_finished()
    return True


def play_game(game_action: GameAction, player_id: str) -> Game:
    TeamService.check_for_existing_team(game_action.team_id)
    check_for_existing_game(game_action.game_id)
    check_if_game_is_active(game_action.game_id)
    if not valid_action_and_action_result(game_action.action, game_action.action_result):
        ex.invalid_action_and_action_result()
    try:
        # REGISTER ACTION: Updates action in DB
        # Is different form updateStatistics method if something goes wrong then
        # statistics will be updated next time this method is called
        game: Game = game_from_player(get_db_client().players.find_one_and_update(
            {"teams.games.game_id": ObjectId(game_action.game_id)},
            {"$inc": {
                f"teams.$[t].games.$[g].{game_action.action}_{game_action.action_result}": 1}},
            array_filters=[
                {"t.team_id": ObjectId(game_action.team_id)},
                {"g.game_id": ObjectId(game_action.game_id)}],
            projection={"teams.games": 1},
            return_document=ReturnDocument.AFTER),
            game_action.game_id)
    except Exception as exception:
        ex.no_data_connection("teamsService/play_game/find_one_and_update/register_action",
                              exception)
    if game is None:
        ex.unable_to_update_game()
    updated_game = update_game_statistics(game)
    updated_game_dict: dict = dict(updated_game)
    try:
        # UPDATED STATISTICS: Updates whole game with updated statistics
        game_to_return: Game = game_from_player(get_db_client().players.find_one_and_update(
            {"teams.games.game_id": ObjectId(game_action.game_id)},
            {"$set": {
                "teams.$[t].games.$[g]": updated_game_dict}},
            array_filters=[
                {"t.team_id": ObjectId(game_action.team_id)},
                {"g.game_id": ObjectId(game_action.game_id)}],
            projection={"teams.games": 1},
            return_document=ReturnDocument.AFTER),
            game_action.game_id)
    except Exception as exception:
        ex.no_data_connection("teamsService/play_game/find_one_and_update/updated_statistics",
                              exception)
    if game_to_return is None:
        ex.unable_to_update_game()
    TeamService.register_game_action(game_action, player_id)
    return game_to_return


def update_game_statistics(game: Game) -> Game:
    game.game_id = ObjectId(game.game_id)
    game.total_attacks = game.attack_points + game.attack_neutrals + game.attack_errors
    game.attack_effectiveness = round(game.attack_points / game.total_attacks, 2) \
        if game.total_attacks > 0 else 0.00
    game.total_blocks = game.block_points + game.block_neutrals + game.block_errors
    game.block_effectiveness = round(game.block_points / game.total_blocks, 2) \
        if game.total_blocks > 0 else 0.00
    game.total_services = game.service_points + game.service_neutrals \
        + game.service_errors
    game.service_effectiveness = round(game.service_points / game.total_services, 2) \
        if game.total_services > 0 else 0.00
    game.total_defenses = game.defense_perfects + game.defense_neutrals + game.defense_errors
    game.defense_effectiveness = round(game.defense_perfects / game.total_defenses, 2) \
        if game.total_defenses > 0 else 0.00
    game.total_receptions = game.reception_perfects + game.reception_neutrals \
        + game.reception_errors
    game.reception_effectiveness = round(game.reception_perfects / game.total_receptions, 2) \
        if game.total_receptions > 0 else 0.00
    game.total_sets = game.set_perfects + game.set_neutrals + game.set_errors
    game.set_effectiveness = round(game.set_perfects / game.total_sets, 2) \
        if game.total_sets > 0 else 0.00
    game.total_points = game.attack_points + game.block_points + game.service_points
    game.total_perfects = game.defense_perfects + game.reception_perfects + game.set_perfects
    game.total_neutrals = game.attack_neutrals + game.block_neutrals + game.service_neutrals \
        + game.defense_neutrals + game.reception_neutrals + game.set_neutrals
    game.total_errors = game.attack_errors + game.block_errors + game.service_errors \
        + game.defense_errors + game.reception_errors + game.set_errors
    game.total_actions = game.total_points + game.total_perfects + game.total_neutrals \
        + game.total_errors
    game.total_effectiveness = round(
        (game.total_points + game.total_perfects) / game.total_actions, 2) \
        if game.total_actions > 0 else 0.00
    return game


def check_for_existing_game(game_id: str) -> None:
    try:
        game: int = get_db_client().players.count_documents(
            {"teams.games.game_id": ObjectId(game_id)})
    except Exception as exception:
        ex.no_data_connection("teamsService/check_for_existing_game/count_documents", exception)
    if game != 1:
        ex.game_not_found()
    LOG.debug(f"Game found: {game_id}.")


def check_for_active_games(teams: list[Team]) -> None:
    for team in teams:
        for game in team.games:
            if game.status == 1:
                ex.active_game(game)
    LOG.debug("No active games found.")


def check_if_game_is_active(game_id: str) -> None:
    try:
        game: Game = game_from_player(get_db_client().players.find_one(
            {"teams.games.game_id": ObjectId(game_id)}, {"teams.games": 1}), game_id)
    except Exception as exception:
        ex.no_data_connection("teamsService/check_if_game_is_active/find_one", exception)
    if game.game_id == game_id and game.status == 0:
        ex.game_already_finished()
    LOG.debug("Game is still active.")


# Validates a proper combination between Action and action_result inputs
def valid_action_and_action_result(action: str, action_result: str) -> bool:
    if action in GAME_ACTIONS[0:3]:
        if action_result == "perfects":
            return False
    elif action in GAME_ACTIONS[3:]:
        if action_result == "points":
            return False
    return True


def validate_game_id(object_id: ObjectId) -> bool:
    # Checks if object_id exists as a team_id in DB
    try:
        teams_count: int = get_db_client().players.count_documents(
            {"teams.team_id": object_id})
    except Exception as exception:
        ex.no_data_connection("gamesService/validate_game_id/count_documents/teams", exception)
    if teams_count > 0:
        return False
    # Checks if object_id exists as a game_id in DB
    try:
        games_count: int = get_db_client().players.count_documents(
            {"teams.games.game_id": object_id})
    except Exception as exception:
        ex.no_data_connection("gamesServices/validate_game_id/count_documents/games", exception)
    if games_count > 0:
        return False
    return True
