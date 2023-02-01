from db.schemas.team import fullTeamSchemas
from db.models.player import Player, PlayerMainInfo

# Schema used for data update operations of one player
def mainInfoPlayerSchema(player) -> PlayerMainInfo:
    return PlayerMainInfo(**({
        "playerId": str(player["_id"]),
        "name": player["name"],
        "surname": player["surname"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "playerCreationDateTime": player["playerCreationDateTime"]
    }))

# Returns entire Player object
def fullPlayerSchema(player) -> Player:
    return Player(**({
        "playerId": str(player["_id"]),
        "name": player["name"],
        "surname": player["surname"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "teams": fullTeamSchemas(player["teams"]) if len(player["teams"]) > 0 else [],
        "playerCreationDateTime": player["playerCreationDateTime"]
    }))

# List of Player objects
def fullPlayerSchemas(players) -> list[Player]:
    return [fullPlayerSchema(player) for player in players]