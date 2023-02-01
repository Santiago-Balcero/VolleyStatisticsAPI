from db.models.team import Team
from db.schemas.game import fullGameSchemas
    
def fullTeamSchema(team) -> Team:
    return Team(**({
        "teamId": str(team["teamId"]),
        "teamName": team["teamName"],
        "teamCategory": team["teamCategory"],
        "games": fullGameSchemas(team["games"]) if len(team["games"]) > 0 else [],
        "teamCreationDateTime": team["teamCreationDateTime"]        
    }))

def fullTeamSchemas(teams) -> list[Team]:
    return [fullTeamSchema(team) for team in teams]

def allTeamsSchemas(players) -> list[Team]:
    teams = []
    for player in players:
        teams += fullTeamSchemas(player["teams"])
    return teams
