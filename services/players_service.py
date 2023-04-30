from bson import ObjectId
from pymongo import ReturnDocument
from models.game_models import GameAction
from models.player_models import NewPlayer, Player, NewPassword, PlayerBase
from models.team_models import Team
from schemas.player_schemas import full_players, full_player
from utils import exceptions as ex
from config.db.client import get_db_client
from config.password.password_context import PASSWORD_CONTEXT
from config.logger.logger import LOG


def get_all_players() -> list[Player]:
    try:
        players: list[Player] = full_players(get_db_client().players.find())
    except Exception as exception:
        ex.no_data_connection("players_service/get_all_players/find", exception)
    return players


def get_player_by_id(player_id: str) -> Player:
    try:
        player: Player = full_player(get_db_client().players.find_one(
            {"_id": ObjectId(player_id)}))
    except Exception as exception:
        ex.no_data_connection("players_service/get_player_by_id/find_one", exception)
    return player


def create_player(player: NewPlayer) -> str:
    if check_player_existence(player.email):
        ex.player_already_exists()
    player.password = PASSWORD_CONTEXT.hash(player.password)
    player_dict: dict = dict(player)
    try:
        player_id: str = get_db_client().players.insert_one(player_dict).inserted_id
    except Exception as exception:
        ex.no_data_connection("players_service/create_player/insert_one", exception)
    if player_id is None:
        ex.unable_to_create_player()
    return player_id


def update_password(new_password: NewPassword, player_id: str) -> bool:
    new_password_hash = PASSWORD_CONTEXT.hash(new_password.new_password)
    try:
        result = get_db_client().players.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": {"password": new_password_hash}})
    except Exception as exception:
        ex.no_data_connection("players_service/update_password/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_update_password()
    return True


def update_player(player: PlayerBase, player_id: str) -> bool:
    try:
        email: str = get_db_client().players.find_one(
            {"_id": ObjectId(player_id)}, {"email": 1})["email"]
    except Exception as exception:
        ex.no_data_connection("players_service/update_player/find_one", exception)
    # Case email was updated
    if email != player.email:
        if check_player_existence(player.email):
            ex.player_already_exists()
    try:
        result = get_db_client().players.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": {
                "first_name": player.first_name, 
                "last_name": player.last_name, 
                "category": player.category, 
                "position": player.position, 
                "email": player.email
            }})
    except Exception as exception:
        ex.no_data_connection("players_service/update_player/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_update_player()
    return True


def delete_player(player_id: str) -> bool:
    try:
        result = get_db_client().players.delete_one({"_id": ObjectId(player_id)})
    except Exception as exception:
        ex.no_data_connection("players_service/delete_player/delete_one", exception)
    if result.deleted_count != 1:
        ex.unable_to_delete_player()
    return True


# Uses email because it is used as username in all app
def check_player_existence(email: str) -> bool:
    try:
        player_exists: int = len(list(get_db_client().players.find({"email": email})))
    except Exception as exception:
        ex.no_data_connection("players_service/check_player_existence/find", exception)
    return player_exists > 0


def sum_player_teams(teams: list[Team], player_id: str) -> None:
    LOG.debug(f"Counting teams for player: {player_id}.")
    teams_number: int = len(teams)
    LOG.debug(f"Total player teams: {teams_number}.")
    try:
        result = get_db_client().players.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": {"total_teams": teams_number}})
    except Exception as exception:
        ex.no_data_connection("players_service/sum_player_teams/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_update_player()
    LOG.debug("Player total teams were updated.")


def sum_player_games(teams: list[Team], player_id: str) -> None:
    LOG.debug(f"Counting games for player: {player_id}.")
    games: int = sum(team.total_games for team in teams)
    LOG.debug(f"Total player games: {games}.")
    try:
        result = get_db_client().players.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": {"total_games": games}})
    except Exception as exception:
        ex.no_data_connection("players_service/sum_player_games/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_update_player()
    LOG.debug("Player total games were updated.")


def register_game_action(game_action: GameAction, player_id: str) -> None:
    LOG.debug(f"Updating player statistics: {player_id}.")
    try:
        # REGISTER ACTION: Updates action in DB
        # Is different form updateStatistics method if something goes wrong then
        # statistics will be updated next time this method is called
        player: Player = full_player(get_db_client().players.find_one_and_update(
            {"_id": ObjectId(player_id)},
            {"$inc": {f"{game_action.action}_{game_action.action_result}": 1}},
            return_document=ReturnDocument.AFTER))
    except Exception as exception:
        ex.no_data_connection(
            "players_service/register_game_action/find_one_and_update/register_action", exception)
    if player is None:
        ex.unable_to_update_player()
    player = update_player_statistics(player)
    try:
        # UPDATED STATISTICS: Updates whole player with updated statistics
        result = get_db_client().players.update_one(
            {"_id": ObjectId(player_id)},
            {"$set": {
                "total_attacks": player.total_attacks,
                "attack_effectiveness": player.attack_effectiveness,
                "total_blocks": player.total_blocks,
                "block_effectiveness": player.block_effectiveness,
                "total_services": player.total_services,
                "service_effectiveness": player.service_effectiveness,
                "total_defenses": player.total_defenses,
                "defense_effectiveness": player.defense_effectiveness,
                "total_receptions": player.total_receptions,
                "reception_effectiveness": player.reception_effectiveness,
                "total_sets": player.total_sets,
                "set_effectiveness": player.set_effectiveness,
                "total_points": player.total_points,
                "total_perfects": player.total_perfects,
                "total_neutrals": player.total_neutrals,
                "total_errors": player.total_errors,
                "total_actions": player.total_actions,
                "total_effectiveness": player.total_effectiveness}})
    except Exception as exception:
        ex.no_data_connection(
            "players_service/register_game_action/find_one_and_update/updated_statistics",
            exception)
    if result.modified_count != 1:
        ex.unable_to_update_game()
    LOG.debug("Player statistics were updated.")


def update_player_statistics(player: Player) -> Player:
    player.total_attacks = player.attack_points + player.attack_neutrals + player.attack_errors
    player.attack_effectiveness = round(player.attack_points / player.total_attacks, 2) \
        if player.total_attacks > 0 else 0.00
    player.total_blocks = player.block_points + player.block_neutrals + player.block_errors
    player.block_effectiveness = round(player.block_points / player.total_blocks, 2) \
        if player.total_blocks > 0 else 0.00
    player.total_services = player.service_points + player.service_neutrals + player.service_errors
    player.service_effectiveness = round(player.service_points / player.total_services, 2) \
        if player.total_services > 0 else 0.00
    player.total_defenses = player.defense_perfects + player.defense_neutrals \
        + player.defense_errors
    player.defense_effectiveness = round(player.defense_perfects / player.total_defenses, 2) \
        if player.total_defenses > 0 else 0.00
    player.total_receptions = player.reception_perfects + player.reception_neutrals \
        + player.reception_errors
    player.reception_effectiveness = round(player.reception_perfects / player.total_receptions, 2) \
        if player.total_receptions > 0 else 0.00
    player.total_sets = player.set_perfects + player.set_neutrals + player.set_errors
    player.set_effectiveness = round(player.set_perfects / player.total_sets, 2) \
        if player.total_sets > 0 else 0.00
    player.total_points = player.attack_points + player.block_points + player.service_points
    player.total_perfects = player.defense_perfects + player.reception_perfects \
        + player.set_perfects
    player.total_neutrals = player.attack_neutrals + player.block_neutrals \
        + player.service_neutrals + player.defense_neutrals + player.reception_neutrals \
        + player.set_neutrals
    player.total_errors = player.attack_errors + player.block_errors + player.service_errors \
        + player.defense_errors + player.reception_errors + player.set_errors
    player.total_actions = player.total_points + player.total_perfects + player.total_neutrals \
        + player.total_errors
    player.total_effectiveness = round(
        (player.total_points + player.total_perfects) / player.total_actions, 2) \
        if player.total_actions > 0 else 0.00
    return player
