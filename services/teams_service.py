from bson import ObjectId
from pymongo import ReturnDocument
from models.game_models import GameAction
from models.team_models import Team, UpdatedTeam
from schemas.team_schemas import all_teams, team_from_player, teams_from_player
from config.db.client import get_db_client
from config.logger.logger import LOG
import services.players_service as PlayerService
from utils import exceptions as ex


def get_all_teams() -> list[Team]:
    try:
        teams: list[Team] = all_teams(get_db_client().players.find({}, {"teams": 1}))
    except Exception as exception:
        ex.no_data_connection("teams_service/get_all_teams/find", exception)
    return teams


def get_teams_by_player(player_id: str) -> list[Team]:
    try:
        teams: list[Team] = teams_from_player(get_db_client().players.find_one(
            {"_id": ObjectId(player_id)},
            {"teams": 1}))
    except Exception as exception:
        ex.no_data_connection("teams_service/get_teams_by_player/find_one", exception)
    if teams is None:
        ex.player_not_found()
    return teams


def get_team_by_id(team_id: str) -> Team:
    if not ObjectId.is_valid(team_id):
        ex.invalid_object_id("team")
    try:
        team: Team = team_from_player(get_db_client().players.find_one(
            {"teams.team_id": ObjectId(team_id)},
            {"teams": 1}),
            team_id)
    except Exception as exception:
        ex.no_data_connection("teams_service/get_team_by_id/find_one", exception)
    if team is None:
        ex.team_not_found()
    return team


def create_team(new_team: Team, player_id: str) -> None:
    try:
        teams: list[Team] = teams_from_player(get_db_client().players.find_one(
            {"_id": ObjectId(player_id)},
            {"teams": 1}))
    except Exception as exception:
        ex.no_data_connection("teams_service/create_team/find_one", exception)
    if teams is None:
        ex.player_not_found()
    check_team_existence(teams, new_team.team_name)
    new_team.team_id = ObjectId()
    while not validate_team_id(new_team.team_id):
        LOG.debug("Repeated team_id in DB, trying again with new value.")
        new_team.team_id = ObjectId()
    new_team_dict = dict(new_team)
    try:
        result = get_db_client().players.update_one(
            {"_id": ObjectId(player_id)},
            {"$push": {"teams": new_team_dict}})
    except Exception as exception:
        ex.no_data_connection("teams_service/create_team/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_create_team()
    teams: list[Team] = get_teams_by_player(player_id)
    PlayerService.sum_player_teams(teams, player_id)


def update_team_name(updated_team: UpdatedTeam) -> None:
    try:
        teams: list[Team] = teams_from_player(get_db_client().players.find_one(
            {"teams.team_id": ObjectId(updated_team.team_id)},
            {"teams": 1}))
    except Exception as exception:
        ex.no_data_connection("teams_service/update_team_name/find_one", exception)
    if teams is None:
        ex.team_not_found()
    check_team_existence(teams, updated_team.new_team_name)
    try:
        result = get_db_client().players.update_one(
            {"teams": {"$elemMatch": {"team_id": ObjectId(updated_team.team_id)}}},
            {"$set": {"teams.$.team_name": updated_team.new_team_name}})
    except Exception as exception:
        ex.no_data_connection("teams_service/update_team_name/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_update_team()


def delete_team(team_id: str, player_id: str) -> None:
    if not ObjectId.is_valid(team_id):
        ex.invalid_object_id("team")
    try:
        teams: list[Team] = teams_from_player(get_db_client().players.find_one(
            {"teams.team_id": ObjectId(team_id)},
            {"teams": 1}))
    except Exception as exception:
        ex.no_data_connection("teams_service/delete_team/find_one", exception)
    if teams is None:
        ex.team_not_found()
    try:
        result = get_db_client().players.update_one(
            {"_id": ObjectId(player_id)},
            {"$pull": {"teams": {"team_id": ObjectId(team_id)}}})
    except Exception as exception:
        ex.no_data_connection("teams_service/delete_team/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_delete_team()


def check_team_existence(teams: list[Team], team_name: str) -> None:
    # Checks if user has another registered team under the same new name
    # If so, raises exception
    for team in teams:
        if team.team_name == team_name:
            ex.team_already_exists()


def check_for_existing_team(team_id: str) -> None:
    if not ObjectId.is_valid(team_id):
        ex.invalid_object_id("team")
    try:
        team: int = get_db_client().players.count_documents({"teams.team_id": ObjectId(team_id)})
    except Exception as exception:
        ex.no_data_connection("teams_service/check_for_existing_team/count_documents", exception)
    if team != 1:
        ex.team_not_found()
    LOG.debug(f"Team found: {team_id}.")


def sum_team_games(team_id: str, player_id: str) -> None:
    LOG.debug(f"Counting games of team: {team_id}.")
    team: Team = get_team_by_id(team_id)
    games: int = len(team.games)
    LOG.debug(f"Total team games: {games}.")
    try:
        result = get_db_client().players.update_one(  
            {"teams": {"$elemMatch": {"team_id": ObjectId(team_id)}}},
            {"$set": {"teams.$.total_games": games}})
    except Exception as exception:
        ex.no_data_connection("teams_service/sum_team_games/update_one", exception)
    if result.modified_count != 1:
        ex.unable_to_update_game()
    LOG.debug("Team total games were updated.")
    teams: list[Team] = get_teams_by_player(player_id)
    PlayerService.sum_player_games(teams, player_id)


def register_game_action(game_action: GameAction, player_id: str) -> None:
    LOG.debug(f"Updating team statistics: {game_action.team_id}.")
    try:
        # REGISTER ACTION: Updates action in DB
        # Is different form updateStatistics method if something goes wrong then
        # statistics will be updated next time this method is called
        team: Team = team_from_player(get_db_client().players.find_one_and_update(
            {"teams": {
                "$elemMatch": {"team_id": ObjectId(game_action.team_id)}}},
            {"$inc": {
                f"teams.$.{game_action.action}_{game_action.action_result}": 1}},
            projection={"teams": 1},
            return_document=ReturnDocument.AFTER), game_action.team_id)
    except Exception as exception:
        ex.no_data_connection(
            "teams_service/register_game_action/find_one_and_update/register_action", exception)
    if team is None:
        ex.unable_to_update_game()
    team = update_team_statistics(team)
    try:
        # UPDATED STATISTICS: Updates whole team with updated statistics
        result = get_db_client().players.update_one(
            {"teams": {"$elemMatch": {"team_id": ObjectId(game_action.team_id)}}},
            {"$set": {
                "teams.$.total_attacks": team.total_attacks,
                "teams.$.attack_effectiveness": team.attack_effectiveness,
                "teams.$.total_blocks": team.total_blocks,
                "teams.$.block_effectiveness": team.block_effectiveness,
                "teams.$.total_services": team.total_services,
                "teams.$.service_effectiveness": team.service_effectiveness,
                "teams.$.total_defenses": team.total_defenses,
                "teams.$.defense_effectiveness": team.defense_effectiveness,
                "teams.$.total_receptions": team.total_receptions,
                "teams.$.reception_effectiveness": team.reception_effectiveness,
                "teams.$.total_sets": team.total_sets,
                "teams.$.set_effectiveness": team.set_effectiveness,
                "teams.$.total_points": team.total_points,
                "teams.$.total_perfects": team.total_perfects,
                "teams.$.total_neutrals": team.total_neutrals,
                "teams.$.total_errors": team.total_errors,
                "teams.$.total_actions": team.total_actions,
                "teams.$.total_effectiveness": team.total_effectiveness}})
    except Exception as exception:
        ex.no_data_connection(
            "teams_service/register_game_action/find_one_and_update/updated_statistics", exception)
    if result.modified_count != 1:
        ex.unable_to_update_game()
    LOG.debug("Team statistics were updated.")
    PlayerService.register_game_action(game_action, player_id)


def update_team_statistics(team: Team) -> Team:
    team.total_attacks = team.attack_points + team.attack_neutrals + team.attack_errors
    team.attack_effectiveness = round(team.attack_points / team.total_attacks, 2) \
        if team.total_attacks > 0 else 0.00
    team.total_blocks = team.block_points + team.block_neutrals + team.block_errors
    team.block_effectiveness = round(team.block_points / team.total_blocks, 2) \
        if team.total_blocks > 0 else 0.00
    team.total_services = team.service_points + team.service_neutrals + team.service_errors
    team.service_effectiveness = round(team.service_points / team.total_services, 2) \
        if team.total_services > 0 else 0.00
    team.total_defenses = team.defense_perfects + team.defense_neutrals + team.defense_errors
    team.defense_effectiveness = round(team.defense_perfects / team.total_defenses, 2) \
        if team.total_defenses > 0 else 0.00
    team.total_receptions = team.reception_perfects + team.reception_neutrals \
        + team.reception_errors
    team.reception_effectiveness = round(team.reception_perfects / team.total_receptions, 2) \
        if team.total_receptions > 0 else 0.00
    team.total_sets = team.set_perfects + team.set_neutrals + team.set_errors
    team.set_effectiveness = round(team.set_perfects / team.total_sets, 2) \
        if team.total_sets > 0 else 0.00
    team.total_points = team.attack_points + team.block_points + team.service_points
    team.total_perfects = team.defense_perfects + team.reception_perfects + team.set_perfects
    team.total_neutrals = team.attack_neutrals + team.block_neutrals + team.service_neutrals \
        + team.defense_neutrals + team.reception_neutrals + team.set_neutrals
    team.total_errors = team.attack_errors + team.block_errors + team.service_errors \
        + team.defense_errors + team.reception_errors + team.set_errors
    team.total_actions = team.total_points + team.total_perfects + team.total_neutrals \
        + team.total_errors
    team.total_effectiveness = round(
        (team.total_points + team.total_perfects) / team.total_actions, 2) \
        if team.total_actions > 0 else 0.00
    return team


def validate_team_id(object_id: ObjectId) -> bool:
    # Checks if object_id exists as a team_id in DB
    try:
        count: int = get_db_client().players.count_documents({"teams.team_id": object_id})
    except Exception as exception:
        ex.no_data_connection("teams_service/validate_team_id/count_documents/teams", exception)
    if count > 0:
        return False
    # Checks if object_id exists as a gameId in DB
    try:
        count: int = get_db_client().players.count_documents({"teams.games.game_id": object_id})
    except Exception as exception:
        ex.no_data_connection("teams_service/validate_team_id/count_documents/games", exception)
    if count > 0:
        return False
    return True
