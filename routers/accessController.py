from fastapi import APIRouter, Depends, status
from utils import exceptions as ex
from config.db.client import dbClient
from schemas.playerSchemas import loginPlayerSchema
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config
from logging.config import dictConfig
import logging
from config.logger.loggerConfig import LogConfig
from models.accessModels import AuthResponse
from services.accessService import loginService, updateToken

router = APIRouter(prefix = "/access", tags = ["Login"])

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

@router.post("/login", status_code = status.HTTP_200_OK, response_model = AuthResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
	log.info(f"Login request for {form.username}.")
	log.debug(f"Data for login request, username: {form.username}, password: {form.password}.")
	return loginService(form.username, form.password)

@router.post("/refresh-token", status_code = status.HTTP_200_OK, response_model = AuthResponse)
async def refreshToken(refresh_token: str):
	log.info(f"Refresh token request.")
	log.debug(f"Refresh token for request: {refresh_token}.")
	return updateToken(refresh_token)
	
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
	return AuthResponse(access_token = token, refresh_token = token2)

def verifyPassword(plainPassword: str, hashedPassword: str):
	return passwordContext.verify(plainPassword, hashedPassword)