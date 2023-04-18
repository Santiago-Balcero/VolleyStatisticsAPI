from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from utils import exceptions as ex
from config.db.client import dbClient
from schemas.playerSchemas import loginPlayerSchema

oauth2 = OAuth2PasswordBearer(tokenUrl = "login")

passwordContext = CryptContext(schemes = ["bcrypt"])

def checkUsernameAndPassword(username: str, password: str) -> str:
	player = dbClient.players.find_one({"email": username}, {"email": 1, "password": 1})
	if player is None:
		ex.wrongCredentials()
	player = loginPlayerSchema(player)
	if not verifyPassword(password, player.password):
		ex.wrongCredentials()
	return player.playerId

def checkIfPlayerExists(playerId: str) -> bool:
    result = dbClient.players.find_one({"_id": ObjectId(playerId)})
    if result is None:
        return False
    return True
  
def verifyPassword(plainPassword: str, hashedPassword: str):
	return passwordContext.verify(plainPassword, hashedPassword)