from fastapi import APIRouter, status, Depends
from routers.access import getCurrentPlayer
from db.models.player import NewPlayer, Player, PlayerMainInfo, UpdatedPlayer
from db.client import dbClient
from db.schemas.player import mainInfoPlayerSchema, fullPlayerSchema, fullPlayerSchemas
from bson import ObjectId
from datetime import datetime
from routers.access import passwordContext

from utils import exceptions as ex

router = APIRouter(prefix = "/players", tags = ["Players"])

# Currently does not depend on AUTH through Depends(getCurrentPlayer) because this is meant to be an ADMIN endpoint
@router.get("", status_code = status.HTTP_200_OK, response_model = list[Player])
async def getAllPlayers():
    players: list[Player] = fullPlayerSchemas(dbClient.players.find())
    if len(players) > 0:
        return players
    ex.noPlayersFound()

@router.get("/{playerId}", status_code = status.HTTP_200_OK, response_model = PlayerMainInfo)
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
    player.password = validPassword(player.password)
    playerDict = dict(player)
    playerDict["playerCreationDateTime"] = datetime.now()
    playerDict["teams"] = []
    id = dbClient.players.insert_one(playerDict).inserted_id
    if not id is None:
        newPlayer = mainInfoPlayerSchema(dbClient.players.find_one({"_id": id}))
        return f"Player {newPlayer.name} {newPlayer.surname} successfully registered with id {newPlayer.playerId}."
    ex.unableToCreatePlayer()
    
@router.put("/password/{playerId}/{newPassword}", status_code = status.HTTP_200_OK, response_model = str)
async def updatePassword(playerId: str, newPassword: str = Depends(getCurrentPlayer)):
    result = dbClient.players.find_one({"_id": ObjectId(playerId)})
    if result is None:
        ex.playerNotFound()
    newPassword = validPassword(newPassword)
    result = dbClient.players.update_one({"_id": ObjectId(playerId)}, {"$set": {"password": newPassword}})
    if result.modified_count == 1:
        return "Password successfully changed."
    ex.unableToUpdatePlayer()
    
@router.put("", status_code = status.HTTP_200_OK, response_model = str)
async def updatePlayer(player: UpdatedPlayer = Depends(getCurrentPlayer)):
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
             "email": player.email}})
    if result.modified_count == 1:
        return f"Player with id {player.playerId} was successfully updated."
    ex.unableToUpdatePlayer()

@router.delete("/{playerId}", status_code = status.HTTP_200_OK, response_model = str)
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
    
def validPassword(p):
    if " " in p or len(p) < 12 or sum(1 for x in p if x.isupper()) == 0 or sum(1 for x in p if x.islower()) == 0 or sum(1 for x in p if x.isdigit()) == 0:
        ex.invalidPassword()
    p = passwordContext.hash(p)
    return p
    
