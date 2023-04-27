from bson import ObjectId
from pymongo import ReturnDocument
from models.gameModels import EndGame, Game, GameAction
from config.db.client import dbClient
from models.teamModels import Team
from schemas.gameSchemas import gameFromPlayer
from schemas.teamSchemas import teamsFromPlayer
from utils import exceptions as ex
import services.teamsService as TeamService
from utils.constants import GAME_ACTIONS
from config.logger.logger import LOG

def getGameById(gameId: str) -> Game:
	if not ObjectId.is_valid(gameId):
		ex.invalidObjectId("game")
	try:
		game: Game = gameFromPlayer(dbClient.players.find_one(
														{"teams.games.gameId": ObjectId(gameId)}, 
														{"teams.games": 1}), 
                              		gameId)
	except Exception as e:
		ex.noDataConnection("gamesService/getGameById/find_one", e)
	if game is None:
		ex.gameNotFound()
	return game

def createGame(teamId: str, newGame: Game, playerId: str) -> bool:
	try:
		teams: list[Team] = teamsFromPlayer(dbClient.players.find_one(
																{"teams.teamId": ObjectId(teamId)}, 
																{"teams": 1}))
	except Exception as e:
		ex.noDataConnection("teamsService/createGame/find_one", e)
	if teams is None:
		ex.teamNotFound()
	TeamService.checkForExistingTeam(teamId)
	# Can´t begin a new match if there are others that have not finished yet
	checkForActiveGames(teams)
	newGame.gameId = ObjectId()
	while not validateGameId(newGame.gameId):
		LOG.debug("Repeated gameId in DB, trying again with new value.")
		newGame.gameId = ObjectId()
	gameDict: dict = dict(newGame)
	try:
		result = dbClient.players.update_one(
									{"teams": {"$elemMatch": {"teamId": ObjectId(teamId)}}}, 
									{"$push": {"teams.$.games": gameDict}})
	except Exception as e:
		ex.noDataConnection("teamsService/createGame/update_one", e)
	if result.modified_count != 1:
		ex.unableToCreateGame()
	TeamService.sumTeamGames(teamId, playerId)
	return True

def finishGame(gameToFinish: EndGame) -> bool:
	TeamService.checkForExistingTeam(gameToFinish.teamId)
	checkForExistingGame(gameToFinish.gameId)
	try:
		result = dbClient.players.update_one(
									{"teams.games.gameId": ObjectId(gameToFinish.gameId)}, 
									{"$set": {"teams.$[t].games.$[g].status": 0}}, 
									array_filters = [
										{"t.teamId": ObjectId(gameToFinish.teamId)}, 
										{"g.gameId": ObjectId(gameToFinish.gameId)}])
	except Exception as e:
		ex.noDataConnection("teamsService/finishGame/update_one", e)
	if result.modified_count != 1:
		ex.gameAlreadyFinished()
	return True

def playGame(gameAction: GameAction, playerId: str) -> Game:
	TeamService.checkForExistingTeam(gameAction.teamId)
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
														return_document = ReturnDocument.AFTER), 
                              		gameAction.gameId)
	except Exception as e:
		ex.noDataConnection("teamsService/playGame/find_one_and_update/registerAction", e)
	if game is None:
		ex.unableToUpdateGame()
	game = updateGameStatistics(game)
	updatedGameDict: dict = dict(game)
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
														return_document = ReturnDocument.AFTER), 
                              		gameAction.gameId)
	except Exception as e:
		ex.noDataConnection("teamsService/playGame/find_one_and_update/updatedStatistics", e)
	if game is None:
		ex.unableToUpdateGame()
	TeamService.registerGameAction(gameAction, playerId)
	return game

def updateGameStatistics(game: Game) -> Game:
	game.gameId = ObjectId(game.gameId)
	game.totalAttacks = game.attackPoints + game.attackNeutrals + game.attackErrors
	game.attackEffectiveness = round(game.attackPoints / game.totalAttacks, 2) if game.totalAttacks > 0 else 0.00
	game.totalBlocks = game.blockPoints + game.blockNeutrals + game.blockErrors
	game.blockEffectiveness = round(game.blockPoints / game.totalBlocks, 2) if game.totalBlocks > 0 else 0.00
	game.totalServices = game.servicePoints + game.serviceNeutrals + game.serviceErrors
	game.serviceEffectiveness = round(game.servicePoints / game.totalServices, 2) if game.totalServices > 0 else 0.00
	game.totalDefenses = game.defensePerfects + game.defenseNeutrals + game.defenseErrors
	game.defenseEffectiveness =  round(game.defensePerfects / game.totalDefenses, 2) if game.totalDefenses > 0 else 0.00
	game.totalReceptions = game.receptionPerfects + game.receptionNeutrals + game.receptionErrors
	game.receptionEffectiveness = round(game.receptionPerfects / game.totalReceptions, 2) if game.totalReceptions > 0 else 0.00
	game.totalSets = game.setPerfects + game.setNeutrals + game.setErrors
	game.setEffectiveness = round(game.setPerfects / game.totalSets, 2) if game.totalSets > 0 else 0.00
	game.totalPoints = game.attackPoints + game.blockPoints + game.servicePoints
	game.totalPerfects = game.defensePerfects + game.receptionPerfects + game.setPerfects
	game.totalNeutrals = game.attackNeutrals + game.blockNeutrals + game.serviceNeutrals + game.defenseNeutrals + game.receptionNeutrals + game.setNeutrals
	game.totalErrors = game.attackErrors + game.blockErrors + game.serviceErrors + game.defenseErrors + game.receptionErrors + game.setErrors
	game.totalActions = game.totalPoints + game.totalPerfects + game.totalNeutrals + game.totalErrors
	game.totalEffectiveness = round((game.totalPoints + game.totalPerfects) / game.totalActions, 2) if game.totalActions > 0 else 0.00
	return game
  
def checkForExistingGame(gameId: str) -> None:
	try:
		game: int = dbClient.players.count_documents({"teams.games.gameId": ObjectId(gameId)})
	except Exception as e:
		ex.noDataConnection("teamsService/checkForExistingGame/count_documents", e)
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
														{"teams.games": 1}), 
                              		gameId)
	except Exception as e:
		ex.noDataConnection("teamsService/checkIfGameIsActive/find_one", e)
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
   
def validateGameId(id: ObjectId) -> bool:
	# Checks if id exists as a teamId in DB
	try:
		count: int = dbClient.players.count_documents({"teams.teamId": id})
	except Exception as e:
		ex.noDataConnection("gamesService/validateGameId/count_documents/teams", e)
	if count > 0:
		return False
	# Checks if id exists as a gameId in DB
	try:
		count: int = dbClient.players.count_documents({"teams.games.gameId": id})
	except Exception as e:
		ex.noDataConnection("gamesServices/validateGameId/count_documents/games", e)
	if count > 0:
		return False
	return True