from datetime import datetime
from bson import ObjectId
from models.playerModels import NewPlayer, Player, PlayerMainInfo, NewPassword, PlayerBase
from schemas.playerSchemas import fullPlayerSchemas, mainInfoPlayerSchema
from config.db.client import dbClient
from utils import exceptions as ex
from utils.passwordContext import PASSWORD_CONTEXT

def getAllPlayers() -> list[Player]:
	try:
		players: list[Player] = fullPlayerSchemas(dbClient.players.find())
	except Exception as e:
		ex.noDataConnection(e)
	if len(players) == 0:
		ex.noPlayersFound()
	return players

def getPlayerById(playerId: str) -> PlayerMainInfo:
	try:
		player: PlayerMainInfo = mainInfoPlayerSchema(dbClient.players.find_one({"_id": ObjectId(playerId)}))
	except Exception as e:
		ex.noDataConnection(e)
	if player is None:
		ex.playerNotFound()
	return player

def createPlayer(player: NewPlayer) -> str:
	if checkPlayerExistance(player.email):
		ex.playerAlreadyExists()
	player.password = PASSWORD_CONTEXT.hash(player.password)
	playerDict: dict = dict(player)
	playerDict["playerCreationDateTime"] = datetime.now()
	playerDict["teams"] = []
	try:
		id: str = dbClient.players.insert_one(playerDict).inserted_id
	except Exception as e:
		ex.noDataConnection(e)
	if id is None:
		ex.unableToCreatePlayer()
	return id

def updatePassword(newPassword: NewPassword, playerId: str) -> bool:
	try:
		player = dbClient.players.find_one({"_id": ObjectId(playerId)})
	except Exception as e:
		ex.noDataConnection(e)
	if player is None:
		ex.playerNotFound()
	password = PASSWORD_CONTEXT.hash(newPassword.newPassword)
	try:
		result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$set": {"password": password}})
	except Exception as e:
		ex.noDataConnection(e)
	if result.modified_count != 1:
		ex.unableToUpdatePassword()
	return True

def updatePlayer(player: PlayerBase, playerId: str) -> bool:
	try:
		email = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"email": 1})["email"]
	except Exception as e:
		ex.noDataConnection(e)
	if email != player.email:
		if checkPlayerExistance(player.email):
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
		ex.noDataConnection(e)
	if result.modified_count != 1:
		ex.unableToUpdatePlayer()
	return True

def deletePlayer(playerId: str) -> bool:
	try:
		result = dbClient.players.delete_one({"_id": ObjectId(playerId)})
	except Exception as e:
		ex.noDataConnection(e)
	if result.deleted_count != 1:
		ex.playerNotFound()
	return True

def checkPlayerExistance(email: str) -> bool:
	try:
		playerExists = len(list(dbClient.players.find({"email": email})))
		return playerExists > 0
	except Exception as e:
		ex.noDataConnection(e)