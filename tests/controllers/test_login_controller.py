from fastapi.testclient import TestClient
from bson import ObjectId
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from main import app
from routers.login_controller import decode_token, create_auth_response
from models.login_models import AuthResponse


client = TestClient(app)


def test_decode_token():
    token: str = config("TEST_TOKEN")
    result = decode_token(token)
    assert ObjectId.is_valid(result)
    assert type(result) == str
    

def test_create_auth_response():
    player_id: str = config("TEST_PLAYER_ID")
    result = create_auth_response(player_id)
    assert type(result) == AuthResponse
