from bson import ObjectId
from models.team_models import Team
from schemas.game_schemas import full_games


def full_team(team: dict) -> Team:
    return Team(**({
        "team_id": str(team["team_id"]),
        "team_name": team["team_name"],
        "team_category": team["team_category"],
        "games": full_games(team["games"]) if len(team["games"]) > 0 else [],
        "total_games": team["total_games"],
        "attack_points": team["attack_points"],
        "attack_neutrals": team["attack_neutrals"],
        "attack_errors": team["attack_errors"],
        "total_attacks": team["total_attacks"],
        "attack_effectiveness": team["attack_effectiveness"],
        "block_points": team["block_points"],
        "block_neutrals": team["block_neutrals"],
        "block_errors": team["block_errors"],
        "total_blocks": team["total_blocks"],
        "block_effectiveness": team["block_effectiveness"],
        "service_points": team["service_points"],
        "service_neutrals": team["service_neutrals"],
        "service_errors": team["service_errors"],
        "total_services": team["total_services"],
        "service_effectiveness": team["service_effectiveness"],
        "defense_perfects": team["defense_perfects"],
        "defense_neutrals": team["defense_neutrals"],
        "defense_errors": team["defense_errors"],
        "total_defenses": team["total_defenses"],
        "defense_effectiveness": team["defense_effectiveness"],
        "reception_perfects": team["reception_perfects"],
        "reception_neutrals": team["reception_neutrals"],
        "reception_errors": team["reception_errors"],
        "total_receptions": team["total_receptions"],
        "reception_effectiveness": team["reception_effectiveness"],
        "set_perfects": team["set_perfects"],
        "set_neutrals": team["set_neutrals"],
        "set_errors": team["set_errors"],
        "total_sets": team["total_sets"],
        "set_effectiveness": team["set_effectiveness"],
        "total_points": team["total_points"],
        "total_perfects": team["total_perfects"],
        "total_neutrals": team["total_neutrals"],
        "total_errors": team["total_errors"],
        "total_actions": team["total_actions"],
        "total_effectiveness": team["total_effectiveness"],
        "team_creation_date_time": team["team_creation_date_time"]
    }))


def full_teams(teams: list[dict]) -> list[Team]:
    return [full_team(team) for team in teams]


def all_teams(players: list[dict]) -> list[Team]:
    teams = []
    for player in players:
        teams += full_teams(player["teams"])
    return teams


def teams_from_player(player: dict) -> list[Team]:
    if player is None:
        return None
    return full_teams(player["teams"]) if len(player["teams"]) > 0 else []


def team_from_player(player: dict, team_id: str) -> Team | None:
    if player is None:
        return None
    for team in player["teams"]:
        if team["team_id"] == ObjectId(team_id):
            return full_team(team)
    return None
