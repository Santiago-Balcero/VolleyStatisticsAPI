from fastapi.testclient import TestClient
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from main import app

client = TestClient(app)


def test_get_all_teams():
    result = client.get("/teams")
    assert result.status_code == 200
    assert type(result.json()["data"]) == list
