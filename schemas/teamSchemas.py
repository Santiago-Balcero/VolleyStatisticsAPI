from bson import ObjectId
from models.teamModels import Team
from schemas.gameSchemas import fullGames

def fullTeam(team: dict) -> Team:
    return Team(**({
        "teamId": str(team["teamId"]),
        "teamName": team["teamName"],
        "teamCategory": team["teamCategory"],
        "games": fullGames(team["games"]) if len(team["games"]) > 0 else [],
        "totalGames": team["totalGames"],
        "attackPoints": team["attackPoints"],
        "attackNeutrals": team["attackNeutrals"],
        "attackErrors": team["attackErrors"],
        "totalAttacks": team["totalAttacks"],
        "attackEffectiveness": team["attackEffectiveness"],
        "blockPoints": team["blockPoints"],
        "blockNeutrals": team["blockNeutrals"],
        "blockErrors": team["blockErrors"],
        "totalBlocks": team["totalBlocks"],
        "blockEffectiveness": team["blockEffectiveness"],
        "servicePoints": team["servicePoints"],
        "serviceNeutrals": team["serviceNeutrals"],
        "serviceErrors": team["serviceErrors"],
        "totalServices": team["totalServices"],
        "serviceEffectiveness": team["serviceEffectiveness"],
        "defensePerfects": team["defensePerfects"],
        "defenseNeutrals": team["defenseNeutrals"],
        "defenseErrors": team["defenseErrors"],
        "totalDefenses": team["totalDefenses"],
        "defenseEffectiveness": team["defenseEffectiveness"],
        "receptionPerfects": team["receptionPerfects"],
        "receptionNeutrals": team["receptionNeutrals"],
        "receptionErrors": team["receptionErrors"],
        "totalReceptions": team["totalReceptions"],
        "receptionEffectiveness": team["receptionEffectiveness"],
        "setPerfects": team["setPerfects"],
        "setNeutrals": team["setNeutrals"],
        "setErrors": team["setErrors"],
        "totalSets": team["totalSets"],
        "setEffectiveness": team["setEffectiveness"],
        "totalPoints": team["totalPoints"],
        "totalPerfects": team["totalPerfects"],
        "totalNeutrals": team["totalNeutrals"],
        "totalErrors": team["totalErrors"],
        "totalActions": team["totalActions"],
        "totalEffectiveness": team["totalEffectiveness"],
        "teamCreationDateTime": team["teamCreationDateTime"]
    }))

def fullTeams(teams: list[dict]) -> list[Team]:
    return [fullTeam(team) for team in teams]

def allTeams(players: list[dict]) -> list[Team]:
    teams = []
    for player in players:
        teams += fullTeams(player["teams"])
    return teams

def teamsFromPlayer(player: dict) -> list[Team]:
    if player is None:
        return None
    return fullTeams(player["teams"]) if len(player["teams"]) > 0 else []

def teamFromPlayer(player: dict, teamId: str) -> Team:
    if player is None:
        return None
    for team in player["teams"]:
        if team["teamId"] == ObjectId(teamId):
            return fullTeam(team)
    return None