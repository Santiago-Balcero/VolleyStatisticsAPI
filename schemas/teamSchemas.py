from models.teamModels import Team
from schemas.gameSchemas import fullGameSchemas
    
def fullTeamSchema(team: dict) -> Team:
    return Team(**({
        "teamId": str(team["teamId"]),
        "teamName": team["teamName"],
        "teamCategory": team["teamCategory"],
        "games": fullGameSchemas(team["games"]) if len(team["games"]) > 0 else [],
        # Sends only date, not time, to Team object
        "teamCreationDateTime": str(team["teamCreationDateTime"]).split(" ")[0]   
    }))

def fullTeamSchemas(teams: list[dict]) -> list[Team]:
    return [fullTeamSchema(team) for team in teams]

def allTeamsSchemas(players: list[dict]) -> list[Team]:
    teams = []
    for player in players:
        teams += fullTeamSchemas(player["teams"])
    return teams