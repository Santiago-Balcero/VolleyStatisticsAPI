from schemas.teamSchemas import fullTeamSchemas
from models.playerModels import Player, PlayerMainInfo, LoginPlayer

# Schema used for data update operations of one player
def mainInfoPlayerSchema(player: dict) -> PlayerMainInfo:
    return PlayerMainInfo(**({
        "playerId": str(player["_id"]),
        "firstName": player["firstName"],
        "lastName": player["lastName"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        # Sends only date, not time, to PlayerMainInfo object
        "playerCreationDateTime": str(player["playerCreationDateTime"]).split(" ")[0],
        "totalGames": player["totalGames"],
        "totalActions": player["totalActions"],
        "totalPoints": player["totalPoints"],
        "totalPerfects": player["totalPerfects"],
        "totalNeutrals": player["totalNeutrals"],
        "totalErrors": player["totalErrors"],
        "totalEffectiveness": player["totalEffectiveness"]
    }))

def loginPlayerSchema(player: dict) -> LoginPlayer:
    return LoginPlayer(**({
        "playerId": str(player["_id"]),
        "email": player["email"],
        "password": player["password"]
    }))

# Returns entire Player object
def fullPlayerSchema(player: dict) -> Player:
    return Player(**({
        "playerId": str(player["_id"]),
        "firstName": player["firstName"],
        "lastName": player["lastName"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "teams": fullTeamSchemas(player["teams"]) if len(player["teams"]) > 0 else [],
        "totalGames": player["totalGames"],
        "totalActions": player["totalActions"],
        "totalPoints": player["totalPoints"],
        "totalPerfects": player["totalPerfects"],
        "totalNeutrals": player["totalNeutrals"],
        "totalErrors": player["totalErrors"],
        "totalEffectiveness": player["totalEffectiveness"],
        "playerCreationDateTime": str(player["playerCreationDateTime"]).split(" ")[0]
    }))

# List of Player objects
def fullPlayerSchemas(players: list[dict]) -> list[Player]:
    return [fullPlayerSchema(player) for player in players]