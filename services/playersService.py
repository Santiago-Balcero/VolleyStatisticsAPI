from bson import ObjectId
from models.playerModels import NewPlayer, Player, PlayerMainInfo, NewPassword, PlayerBase
from schemas.playerSchemas import fullPlayers, mainInfoPlayer
from config.db.client import dbClient
from utils import exceptions as ex
from config.passwordContext.passwordContext import PASSWORD_CONTEXT

def getAllPlayers() -> list[Player]:
	try:
		players: list[Player] = fullPlayers(dbClient.players.find())
	except Exception as e:
		ex.noDataConnection("getAllPlayers/find", e)
	if len(players) == 0:
		ex.noPlayersFound()
	return players

def getPlayerById(playerId: str) -> PlayerMainInfo:
	try:
		player: PlayerMainInfo = mainInfoPlayer(dbClient.players.find_one({"_id": ObjectId(playerId)}))
	except Exception as e:
		ex.noDataConnection("getPlayerById/find_one", e)
	return player

def createPlayer(player: NewPlayer) -> str:
	if checkPlayerExistence(player.email):
		ex.playerAlreadyExists()
	player.password = PASSWORD_CONTEXT.hash(player.password)
	playerDict: dict = dict(player)
	try:
		id: str = dbClient.players.insert_one(playerDict).inserted_id
	except Exception as e:
		ex.noDataConnection("createPlayer/insert_one", e)
	if id is None:
		ex.unableToCreatePlayer()
	return id

def updatePassword(newPassword: NewPassword, playerId: str) -> bool:
	newPasswordHash = PASSWORD_CONTEXT.hash(newPassword.newPassword)
	try:
		result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$set": {"password": newPasswordHash}})
	except Exception as e:
		ex.noDataConnection("updatePassword/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdatePassword()
	return True

def updatePlayer(player: PlayerBase, playerId: str) -> bool:
	try:
		email: str = dbClient.players.find_one({"_id": ObjectId(playerId)}, {"email": 1})["email"]
	except Exception as e:
		ex.noDataConnection("updatePlayer/find_one", e)
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
		ex.noDataConnection("updatePlayer/update_one", e)
	if result.modified_count != 1:
		ex.unableToUpdatePlayer()
	return True

def deletePlayer(playerId: str) -> bool:
	try:
		result = dbClient.players.delete_one({"_id": ObjectId(playerId)})
	except Exception as e:
		ex.noDataConnection("deletePlayer/delete_one", e)
	if result.deleted_count != 1:
		ex.unableToDeletePlayer()
	return True

# Uses email because it is used as username in all app
def checkPlayerExistence(email: str) -> bool:
	try:
		playerExists: int = len(list(dbClient.players.find({"email": email})))
	except Exception as e:
		ex.noDataConnection("checkPlayerExistence/find", e)
	return playerExists > 0