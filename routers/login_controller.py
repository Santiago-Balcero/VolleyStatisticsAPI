from datetime import datetime, timedelta
from decouple import config
from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from bson import ObjectId
from jose import JWTError, jwt
import services.login_service as LoginService
from config.logger.logger import LOG
from models.login_models import AuthResponse, RefreshToken
from utils import exceptions as ex

router = APIRouter(prefix="/access", tags=["Login"])

oauth2 = OAuth2PasswordBearer(tokenUrl="login")

TOKEN_LIFE = int(config("ACCESS_TOKEN_EXPIRE_MINUTES"))
SECRET = config("SECRET")
ALGORITHM = config("ALGORITHM")


async def get_current_player(token: str = Depends(oauth2)) -> str:
    return decode_token(token)


@router.post("/login", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def login(form: OAuth2PasswordRequestForm = Depends()):
    LOG.info(f"Login request for {form.username}.")
    LOG.debug(f"Data for login request, username: {form.username}, password: {form.password}.")
    player_id = LoginService.check_username_and_password(form.username, form.password)
    return create_auth_response(player_id)


@router.post("/refresh-token", status_code=status.HTTP_200_OK, response_model=AuthResponse)
async def update_tokens(refresh_token: RefreshToken):
    LOG.info("Refresh token request.")
    LOG.debug(f"Refresh token for request: {refresh_token.refresh_token}.")
    player_id = decode_token(refresh_token.refresh_token)
    return create_auth_response(player_id)


def create_auth_response(player_id: str) -> AuthResponse:
    access_token = {
        "sub": player_id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_LIFE)
    }
    refresh_token = {
        "sub": player_id,
        "exp": datetime.utcnow() + timedelta(minutes=TOKEN_LIFE * 2)
    }
    token: str = jwt.encode(access_token, SECRET, algorithm=ALGORITHM)
    token2: str = jwt.encode(refresh_token, SECRET, algorithm=ALGORITHM)
    LOG.debug(f"Access Token: {token}")
    LOG.debug(f"Refresh Token: {token2}")
    LOG.info("Access and refresh tokens were created and sent as response.")
    # If user authentication is ok API returns access token
    return AuthResponse(access_token=token, refresh_token=token2)


def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, SECRET, algorithms=[ALGORITHM])
        player_id = payload.get("sub")
        if player_id is None or not ObjectId.is_valid(player_id):
            ex.invalid_token()
        if not LoginService.check_if_player_exists(player_id):
            ex.invalid_token()
    except JWTError:
        ex.invalid_token()
    return player_id
