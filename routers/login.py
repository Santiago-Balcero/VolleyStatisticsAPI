from fastapi import APIRouter, Depends
from utils import exceptions as ex
from db.client import dbClient
from db.schemas.player import loginPlayerSchema
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import jwt, JWTError
from passlib.context import CryptContext
from datetime import datetime, timedelta
from decouple import config

router = APIRouter(prefix = "/access", tags = ["Login"])

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

@router.post("/login")
async def login(form: OAuth2PasswordRequestForm = Depends()):
    result = dbClient.players.find_one({"email": form.username}, {"email": 1, "password": 1})
    if result is None:
        ex.wrongCredentials()
    player = loginPlayerSchema(result)
    if not verifyPassword(form.password, player.password):
        ex.wrongCredentials()
    accessToken = {
        "sub": player.playerId,
        "exp": datetime.utcnow() + timedelta(minutes = TOKEN_LIFE)
    }
    # If user authentication is ok API returns access token
    return {"access_token": jwt.encode(accessToken, SECRET, algorithm = ALGORITHM), "token_type": "bearer"}

def verifyPassword(plainPassword: str, hashedPassword: str):
    return passwordContext.verify(plainPassword, hashedPassword)