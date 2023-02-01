from pydantic import BaseModel, validator, EmailStr
from db.models.team import Team
from utils.constants import PLAYER_POSITIONS, PLAYER_CATEGORIES
from datetime import datetime
from utils import exceptions as ex

class PlayerBase(BaseModel):
    name: str
    surname: str
    category: str # Category on which player plays Men or Women
    position: str
    email: EmailStr
    
    @validator("name")
    def nameValidation(cls, v):
        v = v.strip().title()
        if len(v) < 1:
            raise ValueError("Invalid name.")
        return v
    
    @validator("surname")
    def surnameValidation(cls, v):
        v = v.strip().title()
        if len(v) < 1:
            raise ValueError("Invalid surname.")
        return v
    
    @validator("category")
    def categoryValidation(cls, v):
        v = v.strip().title()
        categories = PLAYER_CATEGORIES
        if v not in categories:
            raise ValueError("Invalid category.")
        return v
    
    @validator("position")
    def positionValidation(cls, v):
        v = v.strip().upper()
        # OH = Outside Hitter, S = Setter, MB = Middle Blocker, L = Libero, O = Opposite spiker
        if v not in PLAYER_POSITIONS:
            raise ValueError("Invalid position.")
        return v

class NewPlayer(PlayerBase):
    password: str

class UpdatedPlayer(PlayerBase):
    playerId: str

class PlayerMainInfo(UpdatedPlayer):
    playerCreationDateTime: datetime
    
class Player(PlayerMainInfo):
    teams: list[Team] = []

class LoginPlayer(BaseModel):
    playerId: str
    email: str
    password: str
    
