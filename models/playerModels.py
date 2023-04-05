from pydantic import BaseModel, validator, EmailStr
from models.teamModels import Team
from utils.constants import PLAYER_POSITIONS, PLAYER_CATEGORIES

class PlayerBase(BaseModel):
    firstName: str
    lastName: str
    category: str # Category on which player plays Men or Women
    position: str
    email: EmailStr
    
    @validator("firstName")
    def firstNameValidation(cls, v):
        v = v.strip().title()
        if len(v) < 1 or len(v) > 30:
            raise ValueError("Invalid first name.")
        return v
    
    @validator("lastName")
    def lastNameValidation(cls, v):
        v = v.strip().title()
        if len(v) < 1 or len(v) > 30:
            raise ValueError("Invalid last name.")
        return v
    
    @validator("category")
    def categoryValidation(cls, v):
        v = v.strip().title()
        if v not in PLAYER_CATEGORIES:
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
    totalGames = 0
    totalActions: int = 0
    totalPoints: int = 0
    totalPerfects: int = 0
    totalNeutrals: int = 0
    totalErrors: int = 0
    totalEffectiveness: float = 0.00
    
    @validator("password")
    def passwordValidation(cls, v):
        return passwordCheck(v)
    
class UpdatedPlayer(PlayerBase):
    playerId: str

class PlayerMainInfo(UpdatedPlayer):
    playerCreationDateTime: str
    totalGames: int
    totalActions: int
    totalPoints: int
    totalPerfects: int
    totalNeutrals: int
    totalErrors: int
    totalEffectiveness: float
    
class Player(PlayerMainInfo):
    teams: list[Team] = []

class LoginPlayer(BaseModel):
    playerId: str
    email: str
    password: str
    
class NewPassword(BaseModel):
	newPassword: str
	
	@validator("newPassword")
	def passwordValidation(cls, v):
		return passwordCheck(v)

def passwordCheck(v):
    v = v.strip()
    if " " in v or len(v) < 12 or sum(1 for x in v if x.isupper()) == 0 or sum(1 for x in v if x.islower()) == 0 or sum(1 for x in v if x.isdigit()) == 0:
        raise ValueError("Invalid password.")
    return v