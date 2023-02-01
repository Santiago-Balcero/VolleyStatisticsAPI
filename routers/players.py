from fastapi import APIRouter, status
from db.models.player import NewPlayer, Player, UpdatedPlayer
from db.client import dbClient
from db.schemas.player import mainInfoPlayerSchema, fullPlayerSchema, fullPlayerSchemas
from bson import ObjectId
from datetime import datetime
from utils import exceptions as ex

router = APIRouter(prefix = "/players", tags = ["Players"])

@router.get("", status_code = status.HTTP_200_OK, response_model = list[Player])
async def getAllPlayers():
    players: list[Player] = fullPlayerSchemas(dbClient.players.find())
    if len(players) > 0:
        return players
    ex.noPlayersFound()

@router.get("/{playerId}", status_code = status.HTTP_200_OK, response_model = Player)
async def getPlayerById(playerId: str):
    result = dbClient.players.find_one({"_id": ObjectId(playerId)})
    if not result is None:
        return fullPlayerSchema(result)
    ex.playerNotFound()

@router.post("", status_code = status.HTTP_201_CREATED, response_model = str)
async def createPlayer(player: NewPlayer):
    if checkPlayerExistance(player.email):
        ex.playerAlreadyExists()
    playerDict = dict(player)
    playerDict["playerCreationDateTime"] = datetime.now()
    playerDict["teams"] = []
    id = dbClient.players.insert_one(playerDict).inserted_id
    if not id is None:
        newPlayer = mainInfoPlayerSchema(dbClient.players.find_one({"_id": id}))
        return f"Player {newPlayer.name} {newPlayer.surname} successfully registered with id {newPlayer.playerId}."
    ex.unableToCreatePlayer()

@router.put("", status_code = status.HTTP_200_OK, response_model = str)
async def updatePlayer(player: UpdatedPlayer):
    email = dbClient.players.find_one({"_id": ObjectId(player.playerId)}, {"email": 1})["email"]
    if email != player.email:
        if checkPlayerExistance(player.email):
            ex.playerAlreadyExists()
    result = dbClient.players.update_one({"_id": ObjectId(player.playerId)}, 
        {"$set": 
            {"name": player.name, 
             "surname": player.surname, 
             "category": player.category, 
             "position": player.position, 
             "email": player.email}}).modified_count
    if result == 1:
        return f"Player with id {player.playerId} was successfully updated."
    ex.unableToUpdatePlayer()

@router.delete("/{playerId}", status_code = status.HTTP_200_OK, response_model = str)
async def deletePlayer(playerId: str):
    if dbClient.players.delete_one({"_id": ObjectId(playerId)}).deleted_count == 1:
        return f"Player with id {playerId} was successfully deleted."
    ex.playerNotFound()

def checkPlayerExistance(email: str) -> bool:
    try:
        playerExists = len(list(dbClient.players.find({"email": email})))
        return playerExists > 0
    except:
        return True
    
