from bson import ObjectId
from models.game_models import Game


def full_game(game: dict) -> Game:
    if game is None:
        return None
    return Game(**({
        "game_id": str(game["game_id"]),
        "game_date_time": game["game_date_time"],
        "status": game["status"],
        "game_country": game["game_country"],
        "game_city": game["game_city"],
        "opponent_team": game["opponent_team"],
        "player_position": game["player_position"],
        "player_number": game["player_number"],
        "attack_points": game["attack_points"],
        "attack_neutrals": game["attack_neutrals"],
        "attack_errors": game["attack_errors"],
        "total_attacks": game["total_attacks"],
        "attack_effectiveness": game["attack_effectiveness"],
        "block_points": game["block_points"],
        "block_neutrals": game["block_neutrals"],
        "block_errors": game["block_errors"],
        "total_blocks": game["total_blocks"],
        "block_effectiveness": game["block_effectiveness"],
        "service_points": game["service_points"],
        "service_neutrals": game["service_neutrals"],
        "service_errors": game["service_errors"],
        "total_services": game["total_services"],
        "service_effectiveness": game["service_effectiveness"],
        "defense_perfects": game["defense_perfects"],
        "defense_neutrals": game["defense_neutrals"],
        "defense_errors": game["defense_errors"],
        "total_defenses": game["total_defenses"],
        "defense_effectiveness": game["defense_effectiveness"],
        "reception_perfects": game["reception_perfects"],
        "reception_neutrals": game["reception_neutrals"],
        "reception_errors": game["reception_errors"],
        "total_receptions": game["total_receptions"],
        "reception_effectiveness": game["reception_effectiveness"],
        "set_perfects": game["set_perfects"],
        "set_neutrals": game["set_neutrals"],
        "set_errors": game["set_errors"],
        "total_sets": game["total_sets"],
        "set_effectiveness": game["set_effectiveness"],
        "total_actions": game["total_actions"],
        "total_points": game["total_points"],
        "total_perfects": game["total_perfects"],
        "total_neutrals": game["total_neutrals"],
        "total_errors": game["total_errors"],
        "total_effectiveness": game["total_effectiveness"]
    }))


def full_games(games: list[dict]) -> list[Game]:
    return [full_game(game) for game in games]


def game_from_player(player: dict, game_id: str) -> Game | None:
    if player is None:
        return None
    for team in player["teams"]:
        for game in team["games"]:
            if game["game_id"] == ObjectId(game_id):
                return full_game(game)
    return None
