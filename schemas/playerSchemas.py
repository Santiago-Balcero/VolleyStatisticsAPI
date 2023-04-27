from schemas.teamSchemas import fullTeams
from models.playerModels import Player, PlayerMainInfo, LoginPlayer

# Schema used for data update operations of one player
def mainInfoPlayer(player: dict) -> PlayerMainInfo:
    return PlayerMainInfo(**({
        "playerId": str(player["_id"]),
        "firstName": player["firstName"],
        "lastName": player["lastName"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "playerCreationDateTime": player["playerCreationDateTime"],
        "totalGames": player["totalGames"],
        "totalActions": player["totalActions"],
        "totalPoints": player["totalPoints"],
        "totalPerfects": player["totalPerfects"],
        "totalNeutrals": player["totalNeutrals"],
        "totalErrors": player["totalErrors"],
        "totalEffectiveness": player["totalEffectiveness"]
    }))

def loginPlayer(player: dict) -> LoginPlayer:
    if player is None:
        return None
    return LoginPlayer(**({
        "playerId": str(player["_id"]),
        "email": player["email"],
        "password": player["password"]
    }))

# Returns entire Player object
def fullPlayer(player: dict) -> Player:
    return Player(**({
        "playerId": str(player["_id"]),
        "firstName": player["firstName"],
        "lastName": player["lastName"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "teams": fullTeams(player["teams"]) if len(player["teams"]) > 0 else [],
        "totalGames": player["totalGames"],
        "totalActions": player["totalActions"],
        "totalPoints": player["totalPoints"],
        "totalPerfects": player["totalPerfects"],
        "totalNeutrals": player["totalNeutrals"],
        "totalErrors": player["totalErrors"],
        "totalEffectiveness": player["totalEffectiveness"],
        "playerCreationDateTime": player["playerCreationDateTime"]
    }))

# List of Player objects
def fullPlayers(players: list[dict]) -> list[Player]:
    return [fullPlayer(player) for player in players]