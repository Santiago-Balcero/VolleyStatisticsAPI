from bson import ObjectId
from models.teamModels import Team, UpdatedTeam
from schemas.teamSchemas import allTeams, teamsFromPlayer

from config.db.client import dbClient
from utils import exceptions as ex

def getAllTeams() -> list[Team]:
	try:
		teams: list[Team] = allTeams(dbClient.players.find({}, {"teams": 1}))
	except Exception as e:
		ex.noDataConnection("getAllTeams/find", e)
	if len(teams) == 0:
		ex.noTeamsFound()
	return teams

def getTeamsByPlayer(playerId: str) -> list[Team]:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"_id": ObjectId(playerId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("getTeamsByPlayer/find_one", e)
	if teams is None:
		ex.playerNotFound()
	return teams

def getTeamById(teamId: str) -> Team:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId("team")
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"teams.teamId": ObjectId(teamId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("getTeamById/find_one", e)
	if teams is None:
		ex.teamNotFound()
	for t in teams:
		if t.teamId == teamId:
			return t

def createTeam(newTeam: Team, playerId: str) -> bool:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"_id": ObjectId(playerId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("createTeam/find_one", e)
	if teams is None:
		ex.playerNotFound()
	checkTeamExistence(teams, newTeam.teamName)
	newTeamDict = dict(newTeam)
	try:
		result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$push": {"teams": newTeamDict}})
	except Exception as e:
		ex.noDataConnection("createTeam/update_one", e)
	if result.modified_count != 1:
		ex.unableToCreateTeam()
	return True

def updateTeamName(updatedTeam: UpdatedTeam, playerId: str) -> bool:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"teams.teamId": ObjectId(updatedTeam.teamId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("updateTeamName/find_one", e)
	if teams is None:
		ex.teamNotFound()
	checkTeamExistence(teams, updatedTeam.newTeamName)
	try:
		result = dbClient.players.update_one(
									{"teams": {"$elemMatch": {"teamId": ObjectId(updatedTeam.teamId)}}},
									{"$set": {"teams.$.teamName": updatedTeam.newTeamName}})
	except Exception as e:
		ex.noDataConnection("updateTeamName/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdateTeam()
	return True

def deleteTeam(teamId: str, playerId: str) -> bool:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId("team")
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"teams.teamId": ObjectId(teamId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("deleteTeam/find_one", e)
	if teams is None:
		ex.teamNotFound()
	try:
		result = dbClient.players.update_one(
									{"_id": ObjectId(playerId)},
									{"$pull": {"teams": {"teamId": ObjectId(teamId)}}})
	except Exception as e:
		ex.noDataConnection("deleteTeam/update_one", e)
	if result.modified_count != 1:
		ex.unableToDeleteTeam()
	return True
	
def checkTeamExistence(teams: list[Team], teamName: str) -> None:
	# Checks if user has another registered team under the same new name
	# If so, raises exception
	for team in teams:
		if team.teamName == teamName:
			ex.teamAlreadyExists()