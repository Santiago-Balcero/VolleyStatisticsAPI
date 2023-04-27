from fastapi import APIRouter, status, Depends
from routers.loginController import getCurrentPlayer
from models.playerModels import NewPlayer, Player, PlayerBase, NewPassword
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

@router.get("/player", status_code = status.HTTP_200_OK, response_model = Player)
async def getPlayerById(playerId: str = Depends(getCurrentPlayer)):
	LOG.info(f"Request for getPlayerById.")
	LOG.debug(f"User: {playerId}.")
	player: Player = PlayerService.getPlayerById(playerId)
	LOG.info("Player info sent as response. Model: Player.")
	return player

# Does not depend on AUTH through Depends(getCurrentPlayer) because this is used for creating new account
@router.post("", status_code = status.HTTP_201_CREATED, response_model = str)
async def createPlayer(player: NewPlayer):
	LOG.info("Request for createPlayer.")    
	newPlayerId: str = PlayerService.createPlayer(player)
	LOG.info("New player created, response sent.")
	LOG.debug(f"New user: {newPlayerId}.")
	return f"Player {player.firstName} {player.lastName} successfully registered."
		
@router.put("/password", status_code = status.HTTP_200_OK, response_model = str)
async def updatePassword(newPassword: NewPassword, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for updatePassword.")
	LOG.debug(f"User: {playerId}.")
	PlayerService.updatePassword(newPassword, playerId)
	LOG.info("Password updated, response sent.")
	return "Password successfully changed."
		
@router.put("", status_code = status.HTTP_200_OK, response_model = str)
async def updatePlayer(player: PlayerBase, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for updatePlayer.")
	LOG.debug(f"User: {playerId}.")
	PlayerService.updatePlayer(player, playerId)
	LOG.info("Player updated, response sent.")
	return f"Player successfully updated."

@router.delete("/delete", status_code = status.HTTP_200_OK, response_model = str)
async def deletePlayer(playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for deletePlayer.")
	LOG.debug(f"User: {playerId}.")
	PlayerService.deletePlayer(playerId)
	LOG.info("Player deleted, response sent.")
	return f"Player successfully deleted."