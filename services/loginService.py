from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from models.playerModels import LoginPlayer
from utils import exceptions as ex
from config.db.client import dbClient
from schemas.playerSchemas import loginPlayer

oauth2 = OAuth2PasswordBearer(tokenUrl = "login")

passwordContext = CryptContext(schemes = ["bcrypt"])

def checkUsernameAndPassword(username: str, password: str) -> str:
	try:
		player: LoginPlayer = loginPlayer(dbClient.players.find_one({"email": username}, {"email": 1, "password": 1}))
	except Exception as e:
		ex.noDataConnection("loginService/checkUsernameAndPassword/find_one", e)
	if player is None:
		ex.wrongCredentials()
	if not verifyPassword(password, player.password):
		ex.wrongCredentials()
	return player.playerId

def checkIfPlayerExists(playerId: str) -> bool:
	try:
		result: int = dbClient.players.count_documents({"_id": ObjectId(playerId)})
	except Exception as e:
		ex.noDataConnection("loginService/checkIfPlayerExists/find_one", e)
	if result != 1:
		return False
	return True

def verifyPassword(plainPassword: str, hashedPassword: str):
	return passwordContext.verify(plainPassword, hashedPassword)