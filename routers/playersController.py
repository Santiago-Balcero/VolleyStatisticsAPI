from fastapi import APIRouter, status, Depends
from routers.loginController import getCurrentPlayer, passwordContext
from models.playerModels import NewPlayer, Player, PlayerMainInfo, UpdatedPlayer, NewPassword
from config.db.client import dbClient
from schemas.playerSchemas import mainInfoPlayerSchema, fullPlayerSchemas
from bson import ObjectId
from datetime import datetime
from logging.config import dictConfig
import logging
from config.logger.loggerConfig import LogConfig

from utils import exceptions as ex

router = APIRouter(prefix = "/players", tags = ["Players"])

dictConfig(LogConfig().dict())
log = logging.getLogger("volleystats")

# Currently does not depend on AUTH through Depends(getCurrentPlayer) 
# because this is meant to be an ADMIN endpoint
@router.get("", status_code = status.HTTP_200_OK, response_model = list[Player])
async def getAllPlayers():
	log.info("Request for getAllPlayers.")
	players: list[Player] = fullPlayerSchemas(dbClient.players.find())
	if len(players) > 0:
		log.info("List of players sent as response. Model: Player.")
		return players
	ex.noPlayersFound()

@router.get("/player", status_code = status.HTTP_200_OK, response_model = PlayerMainInfo)
async def getPlayerById(playerId: str = Depends(getCurrentPlayer)):
	result = dbClient.players.find_one({"_id": ObjectId(playerId)})
	if not result is None:
		return mainInfoPlayerSchema(result)
	ex.playerNotFound()

# Does not depend on AUTH through Depends(getCurrentPlayer) because this is used for creating new account
@router.post("", status_code = status.HTTP_201_CREATED, response_model = str)
async def createPlayer(player: NewPlayer):
	if checkPlayerExistance(player.email):
		ex.playerAlreadyExists()
	player.password = passwordContext.hash(player.password)
	playerDict = dict(player)
	playerDict["playerCreationDateTime"] = datetime.now()
	playerDict["teams"] = []
	id = dbClient.players.insert_one(playerDict).inserted_id
	if not id is None:
		newPlayer = mainInfoPlayerSchema(dbClient.players.find_one({"_id": id}))
		return f"Player {newPlayer.firstName} {newPlayer.lastName} successfully registered."
	ex.unableToCreatePlayer()
		
@router.put("/password", status_code = status.HTTP_200_OK, response_model = str)
async def updatePassword(newPassword: NewPassword, playerId: str = Depends(getCurrentPlayer)):
	log.debug(f"New password: {newPassword.newPassword}")
	result = dbClient.players.find_one({"_id": ObjectId(playerId)})
	if result is None:
		ex.playerNotFound()
	password = passwordContext.hash(newPassword.newPassword)
	result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$set": {"password": password}})
	if result.modified_count == 1:
		return "Password successfully changed."
	ex.unableToUpdatePlayer()
		
@router.put("", status_code = status.HTTP_200_OK, response_model = str)
async def updatePlayer(player: UpdatedPlayer, playerId: str = Depends(getCurrentPlayer)):
	email = dbClient.players.find_one({"_id": ObjectId(player.playerId)}, {"email": 1})["email"]
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
	if result.modified_count == 1:
		return f"Player with id {player.playerId} was successfully updated."
	ex.unableToUpdatePlayer()

@router.delete("/delete", status_code = status.HTTP_200_OK, response_model = str)
async def deletePlayer(playerId: str = Depends(getCurrentPlayer)):
	if dbClient.players.delete_one({"_id": ObjectId(playerId)}).deleted_count == 1:
		return f"Player with id {playerId} was successfully deleted."
	ex.playerNotFound()

def checkPlayerExistance(email: str) -> bool:
	try:
		playerExists = len(list(dbClient.players.find({"email": email})))
		return playerExists > 0
	except:
		return True