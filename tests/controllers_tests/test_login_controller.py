from fastapi.testclient import TestClient
from bson import ObjectId
import sys
import pytest
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from main import app
from routers.login_controller import decode_token, create_auth_response
from models.login_models import AuthResponse


TEST_USERNAME: str = config("TEST_USERNAME")
TEST_PASSWORD: str = config("TEST_PASSWORD")

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


@pytest.mark.parametrize(
    "user, passw, expected",
    [
        (TEST_USERNAME, "abcd1234", {"detail": "Wrong login credentials."}),
        ("fast@calypsa.com", TEST_PASSWORD, {"detail": "Wrong login credentials."}),
        ("dsadasas", "adasd@das", {"detail": "Wrong login credentials."})
    ]
)
def test_wrong_login(user: str, passw: str, expected: dict, database_clean, database_check):
    result = client.post(
        "/auth/login",
        data={
            "username": user,
            "password": passw})
    print(result.json())
    assert result.json() == expected
    if user == TEST_USERNAME and passw == TEST_PASSWORD:
        assert result.json()["access_token"]
        assert result.json()["refresh_token"]


def test_good_login(database_check):
    result = client.post(
        "/auth/login",
        data={
            "username": TEST_USERNAME,
            "password": TEST_PASSWORD})
    assert result.json()["access_token"]
    assert result.json()["refresh_token"]
