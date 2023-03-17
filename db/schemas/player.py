from db.schemas.team import fullTeamSchemas
from db.models.player import Player, PlayerMainInfo, LoginPlayer
from logging.config import dictConfig
import logging
from loggerConfig import LogConfig

dictConfig(LogConfig().dict())
log = logging.getLogger("volleystats")

# Schema used for data update operations of one player
def mainInfoPlayerSchema(player) -> PlayerMainInfo:
    return PlayerMainInfo(**({
        "playerId": str(player["_id"]),
        "name": player["name"],
        "surname": player["surname"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "playerCreationDateTime": str(player["playerCreationDateTime"]).split(" ")[0],
        "totalGames": player["totalGames"],
        "totalActions": player["totalActions"],
        "totalPoints": player["totalPoints"],
        "totalPerfects": player["totalPerfects"],
        "totalNeutrals": player["totalNeutrals"],
        "totalErrors": player["totalErrors"],
        "totalEffectiveness": player["totalEffectiveness"]
    }))

def loginPlayerSchema(player) -> LoginPlayer:
    return LoginPlayer(**({
        "playerId": str(player["_id"]),
        "email": player["email"],
        "password": player["password"]
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