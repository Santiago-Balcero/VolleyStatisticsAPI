from bson import ObjectId
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from models.player_models import LoginPlayer
from utils import exceptions as ex
from config.db.client import get_db_client
from schemas.player_schemas import login_player


oauth2 = OAuth2PasswordBearer(tokenUrl="login")

password_context = CryptContext(schemes=["bcrypt"])


def check_username_and_password(username: str, password: str) -> str:
    try:
        player: LoginPlayer = login_player(
            get_db_client().players.find_one({"email": username}, {"email": 1, "password": 1}))
    except Exception as exception:
        ex.no_data_connection("loginService/checkUsernameAndPassword/find_one", exception)
    if player is None:
        ex.wrong_credentials()
    if not verify_password(password, player.password):
        ex.wrong_credentials()
    return player.player_id


def check_if_player_exists(player_id: str) -> bool:
    try:
        result: int = get_db_client().players.count_documents({"_id": ObjectId(player_id)})
    except Exception as exception:
        ex.no_data_connection("loginService/checkIfPlayerExists/find_one", exception)
    if result != 1:
        return False
    return True


def verify_password(plain_password: str, hashed_password: str):
    return password_context.verify(plain_password, hashed_password)
