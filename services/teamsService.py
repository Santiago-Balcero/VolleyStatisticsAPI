
from datetime import datetime
from bson import ObjectId
from models.teamModels import NewTeam, Team, UpdatedTeam
from schemas.teamSchemas import allTeamsSchemas, fullTeamSchema, fullTeamSchemas
from config.db.client import dbClient
from utils import exceptions as ex

def getAllTeams() -> list[Team]:
	try:
		teams: list[Team] = allTeamsSchemas(dbClient.players.find({}, {"teams": 1}))
	except Exception as e:
		ex.noDataConnection(e)
	if len(teams) == 0:
		ex.noTeamsFound()
	return teams

def getTeamsByPlayer(playerId: str) -> list[Team]:
	try:
		teams = fullTeamSchemas(dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})["teams"])
	except Exception as e:
		ex.noDataConnection(e)
	if teams is None:
		ex.playerNotFound()
	return teams

def getTeamById(teamId: str) -> Team:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId()
	try:
		player = dbClient.players.find_one({"teams.teamId": ObjectId(teamId)}, {"teams": 1})
	except Exception as e:
		ex.noDataConnection(e)
	if player is None:
		ex.teamNotFound()
	for t in player["teams"]:
			if t["teamId"] == ObjectId(teamId):
				team = fullTeamSchema(t)
	return team

def createTeam(newTeam: NewTeam, playerId: str) -> bool:
	try:
		player = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})
	except Exception as e:
		ex.noDataConnection(e)
	if player is None:
		ex.playerNotFound()
	checkTeamExistance(player["teams"], newTeam.teamName)
	newTeamDict = dict(newTeam)
	newTeamDict["teamId"] = ObjectId()
	newTeamDict["games"] = []
	newTeamDict["teamCreationDateTime"] = datetime.now()
	try:
		result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$push": {"teams": newTeamDict}})
	except Exception as e:
		ex.noDataConnection(e)
	if result.modified_count != 1:
		ex.unableToCreateTeam()
	return True

def updateTeamName(updatedTeam: UpdatedTeam, playerId: str) -> bool:
	try:
		player = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})
	except Exception as e:
		ex.noDataConnection(e)
	if player is None:
		ex.playerNotFound()
	checkTeamExistance(player["teams"], updatedTeam.newTeamName)
	try:
		result = dbClient.players.update_one(
		 {"teams": {"$elemMatch": {"teamId": ObjectId(updatedTeam.teamId)}}},
		  {"$set": {"teams.$.teamName": updatedTeam.newTeamName}})
	except Exception as e:
		ex.noDataConnection(e)
	if result.modified_count != 1:
		ex.teamNotFound()
	return True

def deleteTeam(teamId: str, playerId: str) -> bool:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId()
	try:
		player = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1})
	except Exception as e:
		ex.noDataConnection(e)
	if player is None:
		ex.playerNotFound()
	try:
		result = dbClient.players.update_one(
		{"_id": ObjectId(playerId)},
		{"$pull": {"teams": {"teamId": ObjectId(teamId)}}})
	except Exception as e:
		ex.noDataConnection(e)
	if result.modified_count != 1:
		ex.teamNotFound()
	return True
	
def checkTeamExistance(teams: list, teamName: str) -> None:
	# Checks if user has another registered team under the same new name
	# If so, raises exception
	for team in teams:
		if team["teamName"] == teamName:
			ex.teamAlreadyExists()
   