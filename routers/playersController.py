from fastapi import APIRouter, status, Depends
from routers.loginController import getCurrentPlayer, passwordContext
from models.playerModels import NewPlayer, Player, PlayerMainInfo, UpdatedPlayer, NewPassword
from config.db.client import dbClient
import services.playersService as PlayerService
from config.logger.logger import LOG

router = APIRouter(prefix = "/players", tags = ["Players"])

# Currently does not depend on AUTH through Depends(getCurrentPlayer) 
# because this is meant to be an ADMIN endpoint
@router.get("", status_code = status.HTTP_200_OK, response_model = list[Player])
async def getAllPlayers():
	LOG.info("Request for getAllPlayers.")
	players: list[Player] = PlayerService.getAllPlayers()
	LOG.info("List of players sent as response. Model: Player.")
	return players

@router.get("/player", status_code = status.HTTP_200_OK, response_model = PlayerMainInfo)
async def getPlayerById(playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for getPlayerById.")
	player: PlayerMainInfo = PlayerService.getPlayerById(playerId)
	LOG.info("Player info sent as response. Model: PlayerMainInfo.")
	return player

# Does not depend on AUTH through Depends(getCurrentPlayer) because this is used for creating new account
@router.post("", status_code = status.HTTP_201_CREATED, response_model = str)
async def createPlayer(player: NewPlayer):
	LOG.info("Request for createPlayer.")    
	newPlayer: dict = PlayerService.createPlayer(player)
	LOG.info("New player created, response sent.")
	return f"Player {newPlayer.firstName} {newPlayer.lastName} successfully registered."
		
@router.put("/password", status_code = status.HTTP_200_OK, response_model = str)
async def updatePassword(newPassword: NewPassword, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for updatePassword.")
	LOG.debug(f"New password: {newPassword.newPassword}")
	if PlayerService.updatePassword(newPassword, playerId):
		LOG.info("Password updated, response sent.")
		return "Password successfully changed."
		
@router.put("", status_code = status.HTTP_200_OK, response_model = str)
async def updatePlayer(player: UpdatedPlayer, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for updatePlayer")
	if PlayerService.updatePlayer(player, playerId):
		LOG.info("Player updated, response sent.")
		return f"Player with id {playerId} was successfully updated."

@router.delete("/delete", status_code = status.HTTP_200_OK, response_model = str)
async def deletePlayer(playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for deletePlayer")
	if PlayerService.deletePlayer(playerId):
		LOG.info("Player deleted, response sent.")
		return f"Player with id {playerId} was successfully deleted."

def checkPlayerExistance(email: str) -> bool:
	try:
		playerExists = len(list(dbClient.players.find({"email": email})))
		return playerExists > 0
	except:
		return True