from pydantic import BaseModel, validator
from models.gameModels import Game
from utils.constants import TEAM_CATEGORIES
from datetime import datetime

class NewTeam(BaseModel):
    teamName: str
    teamCategory: str
    
    @validator("teamName")
    def teamNameValidation(cls, v):
        v = v.strip().title()
        if len(v) < 1:
            raise ValueError("Invalid team name.")
        return v
    
    @validator("teamCategory")
    def teamCategoryValidation(cls, v):
        v = v.strip().title()
        if v not in TEAM_CATEGORIES:
            raise ValueError("Invalid team category.")
        return v
    
class Team(NewTeam):
    teamId: str
    games: list[Game]
    teamCreationDateTime: datetime
