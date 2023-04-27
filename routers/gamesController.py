from fastapi import APIRouter, status, Depends
from routers.loginController import getCurrentPlayer
from models.gameModels import Game, GameAction, EndGame
import services.gamesService as GameService
from config.logger.logger import LOG

router = APIRouter(prefix = "/games", tags = ["Games"])

@router.get("/{gameId}", status_code = status.HTTP_200_OK, response_model = Game)
async def getGameById(gameId: str, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for getGameById.")
	LOG.debug(f"User: {playerId}. Game: {gameId}.")
	game: Game = GameService.getGameById(gameId)
	LOG.info("Game info sent as response. Model: Game.")
	return game

@router.post("/{teamId}", status_code = status.HTTP_201_CREATED, response_model = str)
async def createGame(teamId: str, newGame: Game, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for createGame.")
	LOG.debug(f"User: {playerId}. Team: {teamId}.")
	GameService.createGame(teamId, newGame, playerId)
	LOG.info("New game created, response sent.")
	LOG.debug(f"New game: {newGame.gameId}")
	return f"Game {newGame.gameId} has started."

@router.put("/finishGame", status_code = status.HTTP_200_OK, response_model = str)
async def finishGame(gameToFinish: EndGame, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for finishGame.")
	LOG.debug(f"User: {playerId}. Team: {gameToFinish.teamId}. Game: {gameToFinish.gameId}.")
	GameService.finishGame(gameToFinish)
	LOG.info("Game finished , response sent.")
	return f"Game with id {gameToFinish.gameId} was finished."
	
@router.put("/playGame", status_code = status.HTTP_200_OK, response_model = dict)
async def playGame(gameAction: GameAction, playerId: str = Depends(getCurrentPlayer)):
    LOG.info("Request for playGame.")
    LOG.debug(f"User: {playerId}. Team: {gameAction.teamId}. Game: {gameAction.gameId}.")
    game: Game = GameService.playGame(gameAction, playerId)
    LOG.info("Game updated, response sent. Model: Game.")
    return game		