from models.gameModels import Game

def gameMainInfoSchema(game) -> dict:
    return {
        "gameId": str(game["gameId"]),
        "gameDateTime": game["gameDateTime"],
        "gameCountry": game["gameCountry"],
        "gameCity": game["gameCity"],
        "status": game["status"],
        "opponentTeam": game["opponentTeam"]
    }
    
def teamGamesMainInfoSchema(games):
    return [gameMainInfoSchema(game) for game in games]

def teamGamesSchema(team):
    return teamGamesMainInfoSchema(team["games"])

def playerGamesSchema(player):
    games = []
    for team in player["teams"]:
        games += (teamGamesSchema(team))
    return games

def fullGameSchema(game) -> Game:
    return Game(**({
        "gameId": str(game["gameId"]),
        "gameDateTime": game["gameDateTime"],
        "status": game["status"],
        "gameCountry": game["gameCountry"],
        "gameCity": game["gameCity"],
        "opponentTeam": game["opponentTeam"],
        "playerPosition": game["playerPosition"],
        "playerNumber": game["playerNumber"],
        "attackPoints": game["attackPoints"],
        "attackNeutrals": game["attackNeutrals"],
        "attackErrors": game["attackErrors"],
        "totalAttacks": game["totalAttacks"],
        "attackEffectiveness": game["attackEffectiveness"],
        "blockPoints": game["blockPoints"],
        "blockNeutrals": game["blockNeutrals"],
        "blockErrors": game["blockErrors"],
        "totalBlocks": game["totalBlocks"],
        "blockEffectiveness": game["blockEffectiveness"],
        "servicePoints": game["servicePoints"],
        "serviceNeutrals": game["serviceNeutrals"],
        "serviceErrors": game["serviceErrors"],
        "totalServices": game["totalServices"],
        "serviceEffectiveness": game["serviceEffectiveness"],
        "defensePerfects": game["defensePerfects"],
        "defenseNeutrals": game["defenseNeutrals"],
        "defenseErrors": game["defenseErrors"],
        "totalDefenses": game["totalDefenses"],
        "defenseEffectiveness": game["defenseEffectiveness"],
        "receptionPerfects": game["receptionPerfects"],
        "receptionNeutrals": game["receptionNeutrals"],
        "receptionErrors": game["receptionErrors"],
        "totalReceptions": game["totalReceptions"],
        "receptionEffectiveness": game["receptionEffectiveness"],
        "setPerfects": game["setPerfects"],
        "setNeutrals": game["setNeutrals"],
        "setErrors": game["setErrors"],
        "totalSets": game["totalSets"],
        "setEffectiveness": game["setEffectiveness"],
        "totalActions": game["totalActions"],
        "totalPoints": game["totalPoints"],
        "totalPerfects": game["totalPerfects"],
        "totalNeutrals": game["totalNeutrals"],
        "totalErrors": game["totalErrors"],
        "totalEffectiveness": game["totalEffectiveness"]
    }))

def fullGameSchemas(games) -> list[Game]:
    [fullGameSchema(game) for game in games]
    