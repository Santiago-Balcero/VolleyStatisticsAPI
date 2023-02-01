from fastapi import APIRouter, status
from db.models.team import Team, NewTeam
from db.client import dbClient
from db.schemas.team import fullTeamSchema, fullTeamSchemas, allTeamsSchemas
from bson import ObjectId
from datetime import datetime
from utils import exceptions as ex

router = APIRouter(prefix = "/teams", tags = ["Teams"])

@router.get("", status_code = status.HTTP_200_OK, response_model = list[Team])
async def getAllTeams():
    teams = allTeamsSchemas(dbClient.players.find({}, {"teams": 1}))
    if len(teams) > 0:
        return teams
    ex.noTeamsFound()

@router.get("/player/{playerId}", status_code = status.HTTP_200_OK, response_model = list[Team])
async def getTeamsByPlayer(playerId: str):
    result = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})
    if not result is None:
        return fullTeamSchemas(result["teams"])
    ex.playerNotFound()

@router.get("/{teamId}", status_code = status.HTTP_200_OK, response_model = Team)
async def getTeamById(teamId: str):
    result = dbClient.players.find_one({"teams.teamId": ObjectId(teamId)}, {"teams": 1})
    if not result is None:
        for team in result["teams"]:
            if team["teamId"] == ObjectId(teamId):
                return fullTeamSchema(team)
    ex.teamNotFound()

@router.post("/{playerId}", status_code = status.HTTP_201_CREATED, response_model = str)
async def createTeam(newTeam: NewTeam, playerId: str):
    result = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})
    if result is None:
        ex.playerNotFound()
    checkTeamExistance(result["teams"], newTeam.teamName)
    newTeamDict = dict(newTeam)
    newTeamDict["teamId"] = ObjectId()
    newTeamDict["games"] = []
    newTeamDict["teamCreationDateTime"] = datetime.now()
    result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$push": {"teams": newTeamDict}})
    if result.modified_count == 1:
        return f"Team {newTeam.teamName} successfully registered."
    ex.unableToCreateTeam()

@router.put("/{playerId}/{teamId}/{teamName}", status_code = status.HTTP_200_OK, response_model = str)
async def updateTeamName(playerId: str, teamId: str, teamName: str):
    teamName = teamName.strip().title()
    result = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})
    if result is None:
        ex.playerNotFound()
    checkTeamExistance(result["teams"], teamName)
    result = dbClient.players.update_one({"teams": {"$elemMatch": {"teamId": ObjectId(teamId)}}}, {"$set": {"teams.$.teamName": teamName}})
    if result.modified_count == 1:
        return f"Team with id {teamId} changed it's name to {teamName}"
    ex.teamNotFound()
        
@router.delete("/{playerId}/{teamId}", status_code = status.HTTP_200_OK, response_model = str)
async def deleteTeam(playerId: str, teamId: str):
    result = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})
    if result is None:
        ex.playerNotFound()
    result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$pull": {"teams": {"teamId": ObjectId(teamId)}}})
    if result.modified_count == 1:
        return f"Team with id {teamId} was successfully deleted."
    ex.teamNotFound()

def checkTeamExistance(teams: list, teamName: str):
    # Checks if user has another registered team under the same new name
    # If so, raises exception
    for team in teams:
        if team["teamName"] == teamName:
            ex.teamAlreadyExists()