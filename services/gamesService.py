from bson import ObjectId
from pymongo import ReturnDocument
from models.gameModels import EndGame, Game, GameAction
from config.db.client import dbClient
from models.teamModels import Team
from schemas.gameSchemas import gameFromPlayer
from schemas.teamSchemas import teamsFromPlayer
from utils import exceptions as ex
import services.teamsService as TeamService
from utils.constants import GAME_ACTIONS, ACTION_RESULTS
from config.logger.logger import LOG

def getGameById(gameId: str) -> Game:
	if not ObjectId.is_valid(gameId):
		ex.invalidObjectId("game")
	try:
		game: Game = gameFromPlayer(dbClient.players.find_one(
														{"teams.games.gameId": ObjectId(gameId)}, 
														{"teams.games": 1}))
	except Exception as e:
		ex.noDataConnection("getGameById/find_one", e)
	if game is None:
		ex.gameNotFound()
	return game

def createGame(teamId: str, newGame: Game, playerId: str) -> bool:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"teams.teamId": ObjectId(teamId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("createGame/find_one", e)
	if teams is None:
		ex.teamNotFound()
	checkForExistingTeam(teamId)
	# Can´t begin a new match if there are others that have not finished yet
	checkForActiveGames(teams)
	gameDict: dict = dict(newGame)
	try:
		result = dbClient.players.update_one(
									{"teams": {"$elemMatch": {"teamId": ObjectId(teamId)}}}, 
									{"$push": {"teams.$.games": gameDict}})
	except Exception as e:
		ex.noDataConnection("createGame/update_one", e)
	if result.modified_count != 1:
		ex.unableToCreateGame()
	TeamService.sumTeamGames(teamId, playerId)
	return True

def finishGame(gameToFinish: EndGame) -> bool:
	checkForExistingTeam(gameToFinish.teamId)
	checkForExistingGame(gameToFinish.gameId)
	try:
		result = dbClient.players.update_one(
									{"teams.games.gameId": ObjectId(gameToFinish.gameId)}, 
									{"$set": {"teams.$[t].games.$[g].status": 0}}, 
									array_filters = [
										{"t.teamId": ObjectId(gameToFinish.teamId)}, 
										{"g.gameId": ObjectId(gameToFinish.gameId)}])
	except Exception as e:
		ex.noDataConnection("finishGame/update_one", e)
	if result.modified_count != 1:
		ex.gameAlreadyFinished()
	return True

def playGame(gameAction: GameAction) -> Game:
	checkForExistingTeam(gameAction.teamId)
	checkForExistingGame(gameAction.gameId)
	checkIfGameIsActive(gameAction.gameId)
	checkForValidActionAndActionResult(gameAction.action, gameAction.actionResult)
	try:
		# REGISTER ACTION: Updates action in DB
		# Is different form updateStatistics method if something goes wrong then
		# statistics will be updated next time this method is called
		game: Game = gameFromPlayer(dbClient.players.find_one_and_update(
														{"teams.games.gameId": ObjectId(gameAction.gameId)}, 
														{"$inc": {
															f"teams.$[t].games.$[g].{gameAction.action}{gameAction.actionResult}": 1}}, 
														array_filters = [
															{"t.teamId": ObjectId(gameAction.teamId)}, 
															{"g.gameId": ObjectId(gameAction.gameId)}], 
														projection = {"teams.games": 1}, 
														return_document = ReturnDocument.AFTER))
	except Exception as e:
		ex.noDataConnection("playGame/find_one_and_update/register_action", e)
	if game is None:
		ex.unableToUpdateGame()
	updatedGameDict = updateGameStatistics(game)
	try:
		# UPDATED STATISTICS: Updates whole game with updated statistics
		game: Game = gameFromPlayer(dbClient.players.find_one_and_update(
														{"teams.games.gameId": ObjectId(gameAction.gameId)}, 
														{"$set": {
															f"teams.$[t].games.$[g]": updatedGameDict}}, 
														array_filters = [
															{"t.teamId": ObjectId(gameAction.teamId)}, 
															{"g.gameId": ObjectId(gameAction.gameId)}], 
														projection = {"teams.games": 1}, 
														return_document = ReturnDocument.AFTER))
	except Exception as e:
		ex.noDataConnection("playGame/find_one_and_update/updated_statistics", e)
	if game is None:
		ex.unableToUpdateGame()
	return game

def updateGameStatistics(game: Game) -> dict:

	game.gameId = ObjectId(game.gameId)
 
	
	
	# Transforms Game to dict to better work with this method
	game: dict = dict(game)

	for action in GAME_ACTIONS:
		if action in ("attack", "block", "service"):
			bestResult: str = "Points"
		else:
			bestResult: str = "Perfects"
		game[f"total{action.title()}s"] = game[f"{action}{bestResult}"] \
										+ game[f"{action}Neutrals"] \
										+ game[f"{action}Errors"]
		game[f"{action}Effectiveness"] = round(game[f"{action}{bestResult}"] \
										/ game[f"total{action.title()}s"], 2) \
										if game[f"total{action.title()}s"] > 0 else 0.00
	for actionResult in ACTION_RESULTS:
		actionResult = actionResult.title()
		if actionResult == "Point":
			game[f"total{actionResult}s"] = game[f"attack{actionResult}s"] \
										+ game[f"block{actionResult}s"] \
										+ game[f"service{actionResult}s"]
		elif actionResult == "Perfect":
			game[f"total{actionResult}s"] = game[f"defense{actionResult}s"] \
										+ game[f"reception{actionResult}s"] \
										+ game[f"set{actionResult}s"]
		else:
			game[f"total{actionResult}s"] = game[f"attack{actionResult}s"] \
										+ game[f"block{actionResult}s"] \
										+ game[f"service{actionResult}s"] \
						  				+ game[f"defense{actionResult}s"] \
								  		+ game[f"reception{actionResult}s"] \
										+ game[f"set{actionResult}s"]
	game["totalActions"] = game["totalPoints"] \
						+ game["totalPerfects"] \
						+ game["totalNeutrals"] \
					  	+ game["totalErrors"]
	game["totalEffectiveness"] = round((game["totalPoints"] \
								+ game["totalPerfects"]) \
				  				/ (game["totalActions"]), 2) \
						  		if game["totalActions"] > 0 else 0.00
	return game
	
def checkForExistingTeam(teamId: str) -> None:
	if not ObjectId.is_valid(teamId):
		ex.invalidObjectId("team")
	try:
		team: int = dbClient.players.count_documents({"teams.teamId": ObjectId(teamId)})
	except Exception as e:
		ex.noDataConnection("checkForExistingTeam/count_documents", e)
	if team != 1:
		ex.teamNotFound()
	LOG.debug(f"Team found: {teamId}.")
  
def checkForExistingGame(gameId: str) -> None:
	try:
		game: int = dbClient.players.count_documents({"teams.games.gameId": ObjectId(gameId)})
	except Exception as e:
		ex.noDataConnection("checkForExistingGame/count_documents", e)
	if game != 1:
		ex.gameNotFound()
	LOG.debug(f"Game found: {gameId}.")

def checkForActiveGames(teams: list[Team]) -> None:
	for team in teams:
		for game in team.games:
			if game.status == 1:
				ex.activeGame(game)
	LOG.debug(f"No active games found.")

def checkIfGameIsActive(gameId: str):
	try:
		game: Game = gameFromPlayer(dbClient.players.find_one(
														{"teams.games.gameId": ObjectId(gameId)}, 
														{"teams.games": 1}))
	except Exception as e:
		ex.noDataConnection("checkIfGameIsActive/find_one", e)
	if game.gameId == gameId and game.status == 0:
		ex.gameAlreadyFinished()
	LOG.debug(f"Game is still active.")
	  
# Validates a proper combination between Action and ActionResult inputs
def checkForValidActionAndActionResult(action: str, actionResult: str):
	if action in GAME_ACTIONS[0:3]:
		if actionResult == "Perfects":
			ex.invalidActionAndActionResult()
	elif action in GAME_ACTIONS[3:]:
		if actionResult == "Points":
			ex.invalidActionAndActionResult()