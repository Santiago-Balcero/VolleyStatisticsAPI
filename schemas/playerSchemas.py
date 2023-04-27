from schemas.teamSchemas import fullTeams
from models.playerModels import Player, LoginPlayer

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
    if player is None:
        return None
    return Player(**({
        "playerId": str(player["_id"]),
        "firstName": player["firstName"],
        "lastName": player["lastName"],
        "category": player["category"],
        "position": player["position"],
        "email": player["email"],
        "teams": fullTeams(player["teams"]) if len(player["teams"]) > 0 else [],
        "totalTeams": player["totalTeams"],
        "attackPoints": player["attackPoints"],
        "attackNeutrals": player["attackNeutrals"],
        "attackErrors": player["attackErrors"],
        "totalAttacks": player["totalAttacks"],
        "attackEffectiveness": player["attackEffectiveness"],
        "blockPoints": player["blockPoints"],
        "blockNeutrals": player["blockNeutrals"],
        "blockErrors": player["blockErrors"],
        "totalBlocks": player["totalBlocks"],
        "blockEffectiveness": player["blockEffectiveness"],
        "servicePoints": player["servicePoints"],
        "serviceNeutrals": player["serviceNeutrals"],
        "serviceErrors": player["serviceErrors"],
        "totalServices": player["totalServices"],
        "serviceEffectiveness": player["serviceEffectiveness"],
        "defensePerfects": player["defensePerfects"],
        "defenseNeutrals": player["defenseNeutrals"],
        "defenseErrors": player["defenseErrors"],
        "totalDefenses": player["totalDefenses"],
        "defenseEffectiveness": player["defenseEffectiveness"],
        "receptionPerfects": player["receptionPerfects"],
        "receptionNeutrals": player["receptionNeutrals"],
        "receptionErrors": player["receptionErrors"],
        "totalReceptions": player["totalReceptions"],
        "receptionEffectiveness": player["receptionEffectiveness"],
        "setPerfects": player["setPerfects"],
        "setNeutrals": player["setNeutrals"],
        "setErrors": player["setErrors"],
        "totalSets": player["totalSets"],
        "setEffectiveness": player["setEffectiveness"],
        "totalGames": player["totalGames"],
        "totalPoints": player["totalPoints"],
        "totalPerfects": player["totalPerfects"],
        "totalNeutrals": player["totalNeutrals"],
        "totalErrors": player["totalErrors"],
        "totalActions": player["totalActions"],
        "totalEffectiveness": player["totalEffectiveness"],
        "playerCreationDateTime": player["playerCreationDateTime"]
    }))

# List of Player objects
def fullPlayers(players: list[dict]) -> list[Player]:
    return [fullPlayer(player) for player in players]