from models.teamModels import Team
from schemas.gameSchemas import fullGames

def fullTeam(team: dict) -> Team:
    return Team(**({
        "teamId": str(team["teamId"]),
        "teamName": team["teamName"],
        "teamCategory": team["teamCategory"],
        "games": fullGames(team["games"]) if len(team["games"]) > 0 else [],
        "totalGames": team["totalGames"],
        "totalActions": team["totalActions"],
        "totalPoints": team["totalPoints"],
        "totalPerfects": team["totalPerfects"],
        "totalNeutrals": team["totalNeutrals"],
        "totalErrors": team["totalErrors"],
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