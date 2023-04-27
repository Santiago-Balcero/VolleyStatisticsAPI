from bson import ObjectId
from pymongo import ReturnDocument
from models.gameModels import GameAction
from models.playerModels import NewPlayer, Player, NewPassword, PlayerBase
from models.teamModels import Team
from schemas.playerSchemas import fullPlayers, fullPlayer
from config.db.client import dbClient
from utils import exceptions as ex
from config.passwordContext.passwordContext import PASSWORD_CONTEXT
from config.logger.logger import LOG

def getAllPlayers() -> list[Player]:
	try:
		players: list[Player] = fullPlayers(dbClient.players.find())
	except Exception as e:
		ex.noDataConnection("playersService/getAllPlayers/find", e)
	if len(players) == 0:
		ex.noPlayersFound()
	return players

def getPlayerById(playerId: str) -> Player:
	try:
		player: Player = fullPlayer(dbClient.players.find_one({"_id": ObjectId(playerId)}))
	except Exception as e:
		ex.noDataConnection("playersService/getPlayerById/find_one", e)
	return player

def createPlayer(player: NewPlayer) -> str:
	if checkPlayerExistence(player.email):
		ex.playerAlreadyExists()
	player.password = PASSWORD_CONTEXT.hash(player.password)
	playerDict: dict = dict(player)
	try:
		id: str = dbClient.players.insert_one(playerDict).inserted_id
	except Exception as e:
		ex.noDataConnection("playersService/createPlayer/insert_one", e)
	if id is None:
		ex.unableToCreatePlayer()
	return id

def updatePassword(newPassword: NewPassword, playerId: str) -> bool:
	newPasswordHash = PASSWORD_CONTEXT.hash(newPassword.newPassword)
	try:
		result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$set": {"password": newPasswordHash}})
	except Exception as e:
		ex.noDataConnection("playersService/updatePassword/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdatePassword()
	return True

def updatePlayer(player: PlayerBase, playerId: str) -> bool:
	try:
		email: str = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"email": 1})["email"]
	except Exception as e:
		ex.noDataConnection("playersService/updatePlayer/find_one", e)
	# Case email was updated
	if email != player.email:
		if checkPlayerExistence(player.email):
			ex.playerAlreadyExists()
	try:
		result = dbClient.players.update_one({"_id": ObjectId(playerId)}, 
				{"$set": {
							"firstName": player.firstName, 
							"lastName": player.lastName, 
							"category": player.category, 
							"position": player.position, 
							"email": player.email
				}})
	except Exception as e:
		ex.noDataConnection("playersService/updatePlayer/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdatePlayer()
	return True

def deletePlayer(playerId: str) -> bool:
	try:
		result = dbClient.players.delete_one({"_id": ObjectId(playerId)})
	except Exception as e:
		ex.noDataConnection("playersService/deletePlayer/delete_one", e)
	if result.deleted_count != 1:
		ex.unableToDeletePlayer()
	return True

# Uses email because it is used as username in all app
def checkPlayerExistence(email: str) -> bool:
	try:
		playerExists: int = len(list(dbClient.players.find({"email": email})))
	except Exception as e:
		ex.noDataConnection("playersService/checkPlayerExistence/find", e)
	return playerExists > 0

def sumPlayerTeams(teams: list[Team], playerId: str) -> None:
	LOG.debug(f"Counting teams for player: {playerId}.")
	teamsNumber: int = len(teams)
	LOG.debug(f"Total player teams: {teamsNumber}.")
	try:
		result = dbClient.players.update_one(
									{"_id": ObjectId(playerId)},
									{"$set": {"totalTeams": teamsNumber}})
	except Exception as e:
		ex.noDataConnection("playersService/sumPlayerTeams/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdatePlayer()
	LOG.debug("Player total teams were updated.")

def sumPlayerGames(teams: list[Team], playerId: str) -> None:
	LOG.debug(f"Counting games for player: {playerId}.")
	games: int = sum(player.totalGames for player in teams)
	LOG.debug(f"Total player games: {games}.")
	try:
		result = dbClient.players.update_one(
									{"_id": ObjectId(playerId)},
									{"$set": {"totalGames": games}})
	except Exception as e:
		ex.noDataConnection("playersService/sumPlayerGames/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdatePlayer()
	LOG.debug("Player total games were updated.")

def registerGameAction(gameAction: GameAction, playerId: str) -> None:
	LOG.debug(f"Updating player statistics: {playerId}.")
	try:
		# REGISTER ACTION: Updates action in DB
		# Is different form updateStatistics method if something goes wrong then
		# statistics will be updated next time this method is called
		player: Player = fullPlayer(dbClient.players.find_one_and_update(
														{"_id": ObjectId(playerId)}, 
														{"$inc": {
															f"{gameAction.action}{gameAction.actionResult}": 1}},
			  											return_document = ReturnDocument.AFTER))
	except Exception as e:
		ex.noDataConnection("playersService/registerGameAction/find_one_and_update/registerAction", e)
	if player is None:
		ex.unableToUpdatePlayer()
	player = updatePlayerStatistics(player)
	try:
		# UPDATED STATISTICS: Updates whole player with updated statistics
		result = dbClient.players.update_one(
      								{"_id": ObjectId(playerId)},
									{"$set": {
										"totalAttacks": player.totalAttacks,
          								"attackEffectiveness": player.attackEffectiveness,
                  						"totalBlocks": player.totalBlocks,
                        				"blockEffectiveness": player.blockEffectiveness,
          								"totalServices": player.totalServices,
                  						"serviceEffectiveness": player.serviceEffectiveness,
                        				"totalDefenses": player.totalDefenses,
          								"defenseEffectiveness": player.defenseEffectiveness,
                  						"totalReceptions": player.totalReceptions,
                        				"receptionEffectiveness": player.receptionEffectiveness,
          								"totalSets": player.totalSets,
                  						"setEffectiveness": player.setEffectiveness,
                        				"totalPoints": player.totalPoints,
          								"totalPerfects": player.totalPerfects,
                  						"totalNeutrals": player.totalNeutrals,
                        				"totalErrors": player.totalErrors,
          								"totalAction": player.totalActions,
                  						"totalEffectiveness": player.totalEffectiveness}})
	except Exception as e:
		ex.noDataConnection("playersService/registerGameAction/find_one_and_update/updatedStatistics", e)
	if result.modified_count != 1:
		ex.unableToUpdateGame()
	LOG.debug("Player statistics were updated.")
 
def updatePlayerStatistics(player: Player) -> Player:
	player.totalAttacks = player.attackPoints + player.attackNeutrals + player.attackErrors
	player.attackEffectiveness = round(player.attackPoints / player.totalAttacks, 2) if player.totalAttacks > 0 else 0.00
	player.totalBlocks = player.blockPoints + player.blockNeutrals + player.blockErrors
	player.blockEffectiveness = round(player.blockPoints / player.totalBlocks, 2) if player.totalBlocks > 0 else 0.00
	player.totalServices = player.servicePoints + player.serviceNeutrals + player.serviceErrors
	player.serviceEffectiveness = round(player.servicePoints / player.totalServices, 2) if player.totalServices > 0 else 0.00
	player.totalDefenses = player.defensePerfects + player.defenseNeutrals + player.defenseErrors
	player.defenseEffectiveness =  round(player.defensePerfects / player.totalDefenses, 2) if player.totalDefenses > 0 else 0.00
	player.totalReceptions = player.receptionPerfects + player.receptionNeutrals + player.receptionErrors
	player.receptionEffectiveness = round(player.receptionPerfects / player.totalReceptions, 2) if player.totalReceptions > 0 else 0.00
	player.totalSets = player.setPerfects + player.setNeutrals + player.setErrors
	player.setEffectiveness = round(player.setPerfects / player.totalSets, 2) if player.totalSets > 0 else 0.00
	player.totalPoints = player.attackPoints + player.blockPoints + player.servicePoints
	player.totalPerfects = player.defensePerfects + player.receptionPerfects + player.setPerfects
	player.totalNeutrals = player.attackNeutrals + player.blockNeutrals + player.serviceNeutrals + player.defenseNeutrals + player.receptionNeutrals + player.setNeutrals
	player.totalErrors = player.attackErrors + player.blockErrors + player.serviceErrors + player.defenseErrors + player.receptionErrors + player.setErrors
	player.totalActions = player.totalPoints + player.totalPerfects + player.totalNeutrals + player.totalErrors
	player.totalEffectiveness = round((player.totalPoints + player.totalPerfects) / player.totalActions, 2) if player.totalActions > 0 else 0.00
	return player
	