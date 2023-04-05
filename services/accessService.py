from fastapi import Depends
from decouple import config
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from utils import exceptions as ex
from jose import jwt, JWTError
from config.db.client import dbClient
from schemas.playerSchemas import loginPlayerSchema
from models.accessModels import AuthResponse
from datetime import datetime, timedelta
from logging.config import dictConfig
import logging
from config.logger.loggerConfig import LogConfig

dictConfig(LogConfig().dict())
log = logging.getLogger("volleystats")

oauth2 = OAuth2PasswordBearer(tokenUrl = "login")

passwordContext = CryptContext(schemes = ["bcrypt"])

TOKEN_LIFE = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET = config("SECRET")
ALGORITHM = config("ALGORITHM")

async def getCurrentPlayer(token: str = Depends(oauth2)):
	try:
		payload = jwt.decode(token, SECRET, algorithms = [ALGORITHM])
		playerId = payload.get("sub")
		if playerId is None:
			ex.wrongCredentials()
	except JWTError:
		ex.wrongCredentials()
	return playerId

def loginService(username: str, password: str) -> AuthResponse:
	result = dbClient.players.find_one({"email": username}, {"email": 1, "password": 1})
	if result is None:
		ex.wrongCredentials()
	player = loginPlayerSchema(result)
	if not verifyPassword(password, player.password):
		ex.wrongCredentials()
	return createAuthResponse(player.playerId)

def updateToken(refreshToken: str) -> AuthResponse:
    playerId = getCurrentPlayer(refreshToken)
    return createAuthResponse(playerId)

def createAuthResponse(playerId: str) -> AuthResponse:
	accessToken = {
		"sub": playerId,
		"exp": datetime.utcnow() + timedelta(minutes = TOKEN_LIFE)
	}
	refreshToken = {
		"sub": playerId,
		"exp": datetime.utcnow() + timedelta(minutes = TOKEN_LIFE * 2)
	}
	token: str = jwt.encode(accessToken, SECRET, algorithm = ALGORITHM)
	token2: str = jwt.encode(refreshToken, SECRET, algorithm = ALGORITHM)
	log.debug(f"Access Token: {token}")
	log.debug(f"Refresh Token: {token2}")
	log.info("Acces and refresh tokens were created and sent as response.")
	# If user authentication is ok API returns access token
	return AuthResponse(accessToken = token, refreshToken = token2)
  
def verifyPassword(plainPassword: str, hashedPassword: str):
	return passwordContext.verify(plainPassword, hashedPassword)