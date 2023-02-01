from fastapi import APIRouter, status
from pymongo import ReturnDocument
from db.models.game import Game
from db.client import dbClient
from db.schemas.game import playerGamesSchema, fullGameSchema
from utils.constants import GAME_ACTIONS, ACTION_RESULTS
from bson import ObjectId
from datetime import datetime
from utils import exceptions as ex

router = APIRouter(prefix = "/games", tags = ["Games"])

@router.get("/{gameId}", status_code = status.HTTP_200_OK, response_model = dict)
async def getGame(gameId: str):
    result = dbClient.players.find_one({"teams.games.gameId": ObjectId(gameId)}, {"teams.games": 1})
    for team in result["teams"]:
       for game in (team["games"]):
           if game["gameId"] == ObjectId(gameId):
               return fullGameSchema(game)

@router.post("/{playerId}/{teamId}", status_code = status.HTTP_201_CREATED, response_model = str)
async def createGame(playerId: str, teamId: str, game: Game):
    # Can´t begin a new match if there are others that have not finished yet
    games = playerGamesSchema(dbClient.players.find_one({"_id": ObjectId(playerId)}, {"teams": 1}))
    checkForActiveGames(games)
    gameDict = dict(game)
    gameDict["gameId"] = ObjectId()
    gameDict["gameDateTime"] = datetime.now()
    gameDict["status"] = 1
    dbClient.players.update_one({"teams": {"$elemMatch": {"teamId": ObjectId(teamId)}}}, {"$push": {"teams.$.games": gameDict}})
    return f"Game started with id {gameDict['gameId']}."

@router.put("/finishgame/{teamId}/{gameId}", status_code = status.HTTP_200_OK, response_model = str)
async def finishGame(teamId: str, gameId: str):
    checkForExistingTeamAndGame(teamId, gameId)
    result = dbClient.players.update_one({"teams.games.gameId": ObjectId(gameId)}, {"$set": {"teams.$[t].games.$[g].status": 0}}, array_filters = [{"t.teamId": ObjectId(teamId)}, {"g.gameId": ObjectId(gameId)}])
    if result.modified_count == 1:
        return f"Game with id {gameId} was finised."
    ex.gameAlreadyFinished()
    
@router.put("/{teamId}/{gameId}/{action}/{actionResult}", status_code = status.HTTP_200_OK, response_model = dict)
async def playGame(teamId: str, gameId: str, action: str, actionResult: str):
    checkForExistingTeamAndGame(teamId, gameId)
    checkIfGameIsActive(gameId)
    action = checkForValidAction(action)
    actionResult = checkForValidActionResult(actionResult)
    result = dbClient.players.find_one_and_update({"teams.games.gameId": ObjectId(gameId)}, {"$inc": {f"teams.$[t].games.$[g].{action}{actionResult}": 1}}, array_filters = [{"t.teamId": ObjectId(teamId)}, {"g.gameId": ObjectId(gameId)}], projection = {"teams.games": 1}, return_document = ReturnDocument.AFTER)
    if result is None:
        ex.unableToUpdateGame()
    for team in result["teams"]:
       for game in (team["games"]):
           if game["gameId"] == ObjectId(gameId):
                updatedGame = updateGameStatistics(game)
                break
    result = dbClient.players.find_one_and_update({"teams.games.gameId": ObjectId(gameId)}, {"$set": {f"teams.$[t].games.$[g]": dict(updatedGame)}}, array_filters = [{"t.teamId": ObjectId(teamId)}, {"g.gameId": ObjectId(gameId)}], projection = {"teams.games": 1}, return_document = ReturnDocument.AFTER)
    if result is None:
        ex.unableToUpdateGame()
    if result is None:
        ex.unableToUpdateGame()
    for team in result["teams"]:
       for game in (team["games"]):
           if game["gameId"] == ObjectId(gameId):
               return fullGameSchema(game)
                    
def updateGameStatistics(game: dict):
    for action in GAME_ACTIONS:
        if action in ("attack", "block", "service"):
            bestResult = "Points"
        else:
            bestResult = "Perfects"
        game[f"total{action.title()}s"] = game[f"{action}{bestResult}"] + game[f"{action}Neutrals"] + game[f"{action}Errors"]
        game[f"{action}Effectiveness"] = round(game[f"{action}{bestResult}"] / game[f"total{action.title()}s"], 2) if game[f"total{action.title()}s"] > 0 else 0.00
    for actionResult in ACTION_RESULTS:
        if actionResult == "Point":
            game[f"total{actionResult}s"] = game[f"attack{actionResult}s"] + game[f"block{actionResult}s"] + game[f"service{actionResult}s"]
        elif actionResult == "Perfect":
            game[f"total{actionResult}s"] = game[f"defense{actionResult}s"] + game[f"reception{actionResult}s"] + game[f"set{actionResult}s"]
        else:
            game[f"total{actionResult}s"] = game[f"attack{actionResult}s"] + game[f"block{actionResult}s"] + game[f"service{actionResult}s"] + game[f"defense{actionResult}s"] + game[f"reception{actionResult}s"] + game[f"set{actionResult}s"]
    game["totalActions"] = game["totalPoints"] + game["totalPerfects"] + game["totalNeutrals"] + game["totalErrors"]
    game["totalEffectiveness"] = round((game["totalPoints"] + game["totalPerfects"]) / (game["totalActions"]), 2) if game["totalActions"] > 0 else 0.00
    return game
    
def checkIfGameIsActive(gameId: str):
    result = dbClient.players.find_one({"teams.games.gameId": ObjectId(gameId)}, {"teams.games": 1})
    for team in result["teams"]:
       for game in (team["games"]):
           if game["gameId"] == ObjectId(gameId) and game["status"] == 0:
               ex.gameAlreadyFinished()

def checkForExistingTeamAndGame(teamId: str, gameId: str):
    team = dbClient.players.count_documents({"teams.teamId": ObjectId(teamId)})
    if team != 1:
        ex.teamNotFound()
    game = dbClient.players.count_documents({"teams.games.gameId": ObjectId(gameId)})
    if game != 1:
        ex.gameNotFound()

def checkForActiveGames(games: list):
    for game in games:
        if game["status"] == 1:
            ex.activeGame(game)
            
def checkForValidAction(action: str):
    action = action.strip().lower()
    if not action in GAME_ACTIONS:
        ex.invalidAction()
    return action

def checkForValidActionResult(result: str):
    result = result.strip()
    if not result in ACTION_RESULTS:
        ex.invalidActionResult()
    return f"{result.title()}s"

