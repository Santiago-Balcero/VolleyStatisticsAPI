from bson import ObjectId
from pymongo import ReturnDocument
from models.gameModels import GameAction
from models.teamModels import Team, UpdatedTeam
from schemas.teamSchemas import allTeams, teamFromPlayer, teamsFromPlayer
from config.db.client import dbClient
import services.playersService as PlayerService
from utils import exceptions as ex
from config.logger.logger import LOG

def getAllTeams() -> list[Team]:
	try:
		teams: list[Team] = allTeams(dbClient.players.find({}, {"teams": 1}))
	except Exception as e:
		ex.noDataConnection("teamsService/getAllTeams/find", e)
	if len(teams) == 0:
		ex.noTeamsFound()
	return teams

def getTeamsByPlayer(playerId: str) -> list[Team]:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"_id": ObjectId(playerId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("teamsService/getTeamsByPlayer/find_one", e)
	if teams is None:
		ex.playerNotFound()
	return teams

def getTeamById(teamId: str) -> Team:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId("team")
	try:
		team: Team = teamFromPlayer(dbClient.players.find_one(
														{"teams.teamId": ObjectId(teamId)}, 
														{"teams": 1}),
							  		teamId)
	except Exception as e:
		ex.noDataConnection("teamsService/getTeamById/find_one", e)
	if team is None:
		ex.teamNotFound()
	return team

def createTeam(newTeam: Team, playerId: str) -> None:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"_id": ObjectId(playerId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("teamsService/createTeam/find_one", e)
	if teams is None:
		ex.playerNotFound()
	checkTeamExistence(teams, newTeam.teamName)
	newTeam.teamId = ObjectId()
	while not validateTeamId(newTeam.teamId):
		LOG.debug("Repeated teamId in DB, trying again with new value.")
		newTeam.teamId = ObjectId()
	newTeamDict = dict(newTeam)
	try:
		result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$push": {"teams": newTeamDict}})
	except Exception as e:
		ex.noDataConnection("teamsService/createTeam/update_one", e)
	if result.modified_count != 1:
		ex.unableToCreateTeam()
	teams: list[Team] = getTeamsByPlayer(playerId)
	PlayerService.sumPlayerTeams(teams, playerId)

def updateTeamName(updatedTeam: UpdatedTeam) -> None:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"teams.teamId": ObjectId(updatedTeam.teamId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("teamsService/updateTeamName/find_one", e)
	if teams is None:
		ex.teamNotFound()
	checkTeamExistence(teams, updatedTeam.newTeamName)
	try:
		result = dbClient.players.update_one(
									{"teams": {"$elemMatch": {"teamId": ObjectId(updatedTeam.teamId)}}},
									{"$set": {"teams.$.teamName": updatedTeam.newTeamName}})
	except Exception as e:
		ex.noDataConnection("teamsService/updateTeamName/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdateTeam()

def deleteTeam(teamId: str, playerId: str) -> None:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId("team")
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"teams.teamId": ObjectId(teamId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("teamsService/deleteTeam/find_one", e)
	if teams is None:
		ex.teamNotFound()
	try:
		result = dbClient.players.update_one(
									{"_id": ObjectId(playerId)},
									{"$pull": {"teams": {"teamId": ObjectId(teamId)}}})
	except Exception as e:
		ex.noDataConnection("teamsService/deleteTeam/update_one", e)
	if result.modified_count != 1:
		ex.unableToDeleteTeam()
	
def checkTeamExistence(teams: list[Team], teamName: str) -> None:
	# Checks if user has another registered team under the same new name
	# If so, raises exception
	for team in teams:
		if team.teamName == teamName:
			ex.teamAlreadyExists()
   
def checkForExistingTeam(teamId: str) -> None:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId("team")
	try:
		team: int = dbClient.players.count_documents({"teams.teamId": ObjectId(teamId)})
	except Exception as e:
		ex.noDataConnection("teamsService/checkForExistingTeam/count_documents", e)
	if team != 1:
		ex.teamNotFound()
	LOG.debug(f"Team found: {teamId}.")
   
def sumTeamGames(teamId: str, playerId: str) -> None:
	LOG.debug(f"Counting games of team: {teamId}.")
	team: Team = getTeamById(teamId)
	games: int = len(team.games)
	LOG.debug(f"Total team games: {games}.")
	try:
		result = dbClient.players.update_one(  
									{"teams": {"$elemMatch": {"teamId": ObjectId(teamId)}}},
									{"$set": {"teams.$.totalGames": games}})
	except Exception as e:
		ex.noDataConnection("teamsService/sumTeamGames/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdateGame
	LOG.debug("Team total games were updated.")
	teams: list[Team] = getTeamsByPlayer(playerId)
	PlayerService.sumPlayerGames(teams, playerId)
 
def registerGameAction(gameAction: GameAction, playerId: str) -> None:
	LOG.debug(f"Updating team statistics: {gameAction.teamId}.")
	try:
		# REGISTER ACTION: Updates action in DB
		# Is different form updateStatistics method if something goes wrong then
		# statistics will be updated next time this method is called
		team: Team = teamFromPlayer(dbClient.players.find_one_and_update(
														{"teams": {
                  											"$elemMatch": {"teamId": ObjectId(gameAction.teamId)}}}, 
														{"$inc": {
															f"teams.$.{gameAction.action}{gameAction.actionResult}": 1}},
														projection = {"teams": 1},
			  											return_document = ReturnDocument.AFTER),
							  		gameAction.teamId)
	except Exception as e:
		ex.noDataConnection("teamsService/registerGameAction/find_one_and_update/registerAction", e)
	if team is None:
		ex.unableToUpdateGame()
	team = updateTeamStatistics(team)
	try:
		# UPDATED STATISTICS: Updates whole team with updated statistics
		result = dbClient.players.update_one(
    								{"teams": {"$elemMatch": {"teamId": ObjectId(gameAction.teamId)}}},
									{"$set": {
										"teams.$.totalAttacks": team.totalAttacks,
          								"teams.$.attackEffectiveness": team.attackEffectiveness,
                  						"teams.$.totalBlocks": team.totalBlocks,
                        				"teams.$.blockEffectiveness": team.blockEffectiveness,
          								"teams.$.totalServices": team.totalServices,
                  						"teams.$.serviceEffectiveness": team.serviceEffectiveness,
                        				"teams.$.totalDefenses": team.totalDefenses,
          								"teams.$.defenseEffectiveness": team.defenseEffectiveness,
                  						"teams.$.totalReceptions": team.totalReceptions,
                        				"teams.$.receptionEffectiveness": team.receptionEffectiveness,
          								"teams.$.totalSets": team.totalSets,
                  						"teams.$.setEffectiveness": team.setEffectiveness,
                        				"teams.$.totalPoints": team.totalPoints,
          								"teams.$.totalPerfects": team.totalPerfects,
                  						"teams.$.totalNeutrals": team.totalNeutrals,
                        				"teams.$.totalErrors": team.totalErrors,
          								"teams.$.totalAction": team.totalActions,
                  						"teams.$.totalEffectiveness": team.totalEffectiveness}})
	except Exception as e:
		ex.noDataConnection("teamsService/registerGameAction/find_one_and_update/updatedStatistics", e)
	if result.modified_count != 1:
		ex.unableToUpdateGame()
	LOG.debug("Team statistics were updated.")
	PlayerService.registerGameAction(gameAction, playerId)

def updateTeamStatistics(team: Team) -> Team:
	team.totalAttacks = team.attackPoints + team.attackNeutrals + team.attackErrors
	team.attackEffectiveness = round(team.attackPoints / team.totalAttacks, 2) if team.totalAttacks > 0 else 0.00
	team.totalBlocks = team.blockPoints + team.blockNeutrals + team.blockErrors
	team.blockEffectiveness = round(team.blockPoints / team.totalBlocks, 2) if team.totalBlocks > 0 else 0.00
	team.totalServices = team.servicePoints + team.serviceNeutrals + team.serviceErrors
	team.serviceEffectiveness = round(team.servicePoints / team.totalServices, 2) if team.totalServices > 0 else 0.00
	team.totalDefenses = team.defensePerfects + team.defenseNeutrals + team.defenseErrors
	team.defenseEffectiveness =  round(team.defensePerfects / team.totalDefenses, 2) if team.totalDefenses > 0 else 0.00
	team.totalReceptions = team.receptionPerfects + team.receptionNeutrals + team.receptionErrors
	team.receptionEffectiveness = round(team.receptionPerfects / team.totalReceptions, 2) if team.totalReceptions > 0 else 0.00
	team.totalSets = team.setPerfects + team.setNeutrals + team.setErrors
	team.setEffectiveness = round(team.setPerfects / team.totalSets, 2) if team.totalSets > 0 else 0.00
	team.totalPoints = team.attackPoints + team.blockPoints + team.servicePoints
	team.totalPerfects = team.defensePerfects + team.receptionPerfects + team.setPerfects
	team.totalNeutrals = team.attackNeutrals + team.blockNeutrals + team.serviceNeutrals + team.defenseNeutrals + team.receptionNeutrals + team.setNeutrals
	team.totalErrors = team.attackErrors + team.blockErrors + team.serviceErrors + team.defenseErrors + team.receptionErrors + team.setErrors
	team.totalActions = team.totalPoints + team.totalPerfects + team.totalNeutrals + team.totalErrors
	team.totalEffectiveness = round((team.totalPoints + team.totalPerfects) / team.totalActions, 2) if team.totalActions > 0 else 0.00
	return team

def validateTeamId(id: ObjectId) -> bool:
	# Checks if id exists as a teamId in DB
	try:
		count: int = dbClient.players.count_documents({"teams.teamId": id})
	except Exception as e:
		ex.noDataConnection("teamsService/validateTeamId/count_documents/teams", e)
	if count > 0:
		return False
	# Checks if id exists as a gameId in DB
	try:
		count: int = dbClient.players.count_documents({"teams.games.gameId": id})
	except Exception as e:
		ex.noDataConnection("teamsService/validateTeamId/count_documents/games", e)
	if count > 0:
		return False
	return True
