from datetime import datetime
from bson import ObjectId
from models.playerModels import NewPlayer, Player, PlayerMainInfo, NewPassword, UpdatedPlayer
from schemas.playerSchemas import fullPlayerSchemas, mainInfoPlayerSchema
from config.db.client import dbClient
from utils import exceptions as ex
from utils.passwordContext import PASSWORD_CONTEXT

def getAllPlayers() -> list[Player]:
	players: list[Player] = fullPlayerSchemas(dbClient.players.find())
	if len(players) == 0:
		ex.noPlayersFound()
	return players

def getPlayerById(playerId: str) -> PlayerMainInfo:
	player: PlayerMainInfo = mainInfoPlayerSchema(dbClient.players.find_one({"_id": ObjectId(playerId)}))
	if player is None:
		ex.playerNotFound()
	return player

def createPlayer(player: NewPlayer) -> dict:
	if checkPlayerExistance(player.email):
		ex.playerAlreadyExists()
	player.password = PASSWORD_CONTEXT.hash(player.password)
	playerDict: dict = dict(player)
	playerDict["playerCreationDateTime"] = datetime.now()
	playerDict["teams"] = []
	id: str = dbClient.players.insert_one(playerDict).inserted_id
	if id is None:
		ex.unableToCreatePlayer()
	newPlayer: dict = mainInfoPlayerSchema(dbClient.players.find_one({"_id": id}))
	return newPlayer

def updatePassword(newPassword: NewPassword, playerId: str) -> bool:
	player = dbClient.players.find_one({"_id": ObjectId(playerId)})
	if player is None:
		ex.playerNotFound()
	password = PASSWORD_CONTEXT.hash(newPassword.newPassword)
	result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$set": {"password": password}})
	if result.modified_count != 1:
		ex.unableToUpdatePassword()
	return True

def updatePlayer(player: UpdatedPlayer, playerId: str) -> bool:
	email = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"email": 1})["email"]
	if email != player.email:
		if checkPlayerExistance(player.email):
			ex.playerAlreadyExists()
	result = dbClient.players.update_one({"_id": ObjectId(player.playerId)}, 
			{"$set": {
	   					"firstName": player.firstName, 
	 					"lastName": player.lastName, 
						"category": player.category, 
						"position": player.position, 
						"email": player.email
	  		}})
	if result.modified_count != 1:
		ex.unableToUpdatePlayer()
	return True

def deletePlayer(playerId: str) -> bool:
	if dbClient.players.delete_one({"_id": ObjectId(playerId)}).deleted_count != 1:
		ex.playerNotFound()
	return True

def checkPlayerExistance(email: str) -> bool:
	try:
		playerExists = len(list(dbClient.players.find({"email": email})))
		return playerExists > 0
	except:
		return True