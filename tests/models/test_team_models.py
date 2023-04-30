import pydantic
import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from models.team_models import Team, UpdatedTeam


@pytest.mark.parametrize(
    "team_n, team_c",
    [
        ("Vakif", "x"),
        ("", "Men"),
    ])   
def test_team_validation_error(
        team_n: str,
        team_c: str):
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        team = Team(
            team_name=team_n,
            team_category=team_c)
        print(team)


@pytest.mark.parametrize(
    "team_i, new_team_n",
    [
        ("ajlkasdj", "Dynavit"),
        ("644dde8022e3a5c85d0e506b", "")
    ])
def test_updated_team_validation_error(
        team_i: str,
        new_team_n: str):
    with pytest.raises(pydantic.error_wrappers.ValidationError):
        updated_team = UpdatedTeam(
            team_id=team_i,
            new_team_name=new_team_n)
        print(updated_team)
