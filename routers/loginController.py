from bson import ObjectId
from fastapi import APIRouter, Depends, status
from utils import exceptions as ex
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from datetime import datetime, timedelta
from decouple import config
from models.loginModels import AuthResponse, RefreshToken
import services.loginService as LoginService
from config.passwordContext.passwordContext import PASSWORD_CONTEXT
from config.logger.logger import LOG

router = APIRouter(prefix = "/access", tags = ["Login"])

oauth2 = OAuth2PasswordBearer(tokenUrl = "login")

TOKEN_LIFE = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET = config("SECRET")
ALGORITHM = config("ALGORITHM")

async def getCurrentPlayer(token: str = Depends(oauth2)):
	return decodeToken(token)

@router.post("/login", status_code = status.HTTP_200_OK, response_model = AuthResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
	LOG.info(f"Login request for {form.username}.")
	LOG.debug(f"Data for login request, username: {form.username}, password: {form.password}.")
	playerId = LoginService.checkUsernameAndPassword(form.username, form.password)
	return createAuthResponse(playerId)

@router.post("/refresh-token", status_code = status.HTTP_200_OK, response_model = AuthResponse)
async def updateTokens(refreshToken: RefreshToken):
	LOG.info(f"Refresh token request.")
	LOG.debug(f"Refresh token for request: {refreshToken.refreshToken}.")
	playerId = decodeToken(refreshToken.refreshToken)
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
	LOG.debug(f"Access Token: {token}")
	LOG.debug(f"Refresh Token: {token2}")
	LOG.info("Access and refresh tokens were created and sent as response.")
	# If user authentication is ok API returns access token
	return AuthResponse(accessToken = token, refreshToken = token2)

def verifyPassword(plainPassword: str, hashedPassword: str):
	return PASSWORD_CONTEXT.verify(plainPassword, hashedPassword)

def decodeToken(token: str):
	try:
		payload = jwt.decode(token, SECRET, algorithms = [ALGORITHM])
		playerId = payload.get("sub")
		if playerId is None or not ObjectId.is_valid(playerId):
			ex.invalidToken()
		if not LoginService.checkIfPlayerExists(playerId):
			ex.invalidToken()
	except JWTError:
		ex.invalidToken()
	return playerId