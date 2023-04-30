from schemas.team_schemas import full_teams
from models.player_models import Player, LoginPlayer


def login_player(player: dict) -> LoginPlayer:
    if player is None:
        return None
    return LoginPlayer(**({
        "player_id": str(player["_id"]),
        "email": player["email"],
        "password": player["password"]
    }))


# Returns entire Player object
def full_player(player: dict) -> Player:
    if player is None:
        return None
    return Player(**({
        "player_id": str(player["_id"]),
        "first_name": player["first_name"],
        "last_name": player["last_name"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "teams": full_teams(player["teams"]) if len(player["teams"]) > 0 else [],
        "total_teams": player["total_teams"],
        "attack_points": player["attack_points"],
        "attack_neutrals": player["attack_neutrals"],
        "attack_errors": player["attack_errors"],
        "total_attacks": player["total_attacks"],
        "attack_effectiveness": player["attack_effectiveness"],
        "block_points": player["block_points"],
        "block_neutrals": player["block_neutrals"],
        "block_errors": player["block_errors"],
        "total_blocks": player["total_blocks"],
        "block_effectiveness": player["block_effectiveness"],
        "service_points": player["service_points"],
        "service_neutrals": player["service_neutrals"],
        "service_errors": player["service_errors"],
        "total_services": player["total_services"],
        "service_effectiveness": player["service_effectiveness"],
        "defense_perfects": player["defense_perfects"],
        "defense_neutrals": player["defense_neutrals"],
        "defense_errors": player["defense_errors"],
        "total_defenses": player["total_defenses"],
        "defense_effectiveness": player["defense_effectiveness"],
        "reception_perfects": player["reception_perfects"],
        "reception_neutrals": player["reception_neutrals"],
        "reception_errors": player["reception_errors"],
        "total_receptions": player["total_receptions"],
        "reception_effectiveness": player["reception_effectiveness"],
        "set_perfects": player["set_perfects"],
        "set_neutrals": player["set_neutrals"],
        "set_errors": player["set_errors"],
        "total_sets": player["total_sets"],
        "set_effectiveness": player["set_effectiveness"],
        "total_games": player["total_games"],
        "total_points": player["total_points"],
        "total_perfects": player["total_perfects"],
        "total_neutrals": player["total_neutrals"],
        "total_errors": player["total_errors"],
        "total_actions": player["total_actions"],
        "total_effectiveness": player["total_effectiveness"],
        "player_creation_date_time": player["player_creation_date_time"]
    }))


# List of Player objects
def full_players(players: list[dict]) -> list[Player]:
    return [full_player(player) for player in players]
