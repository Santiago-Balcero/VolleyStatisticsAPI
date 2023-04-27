from datetime import datetime
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
	attackPoints: int = 0
	attackNeutrals: int = 0
	attackErrors: int = 0
	totalAttacks: int = 0
	attackEffectiveness: float = 0.00
	blockPoints: int = 0
	blockNeutrals: int = 0
	blockErrors: int = 0
	totalBlocks: int = 0
	blockEffectiveness: float = 0.00
	servicePoints: int = 0
	serviceNeutrals:int = 0
	serviceErrors: int = 0
	totalServices: int = 0
	serviceEffectiveness: float = 0.00
	defensePerfects: int = 0
	defenseNeutrals: int = 0
	defenseErrors: int = 0
	totalDefenses: int = 0
	defenseEffectiveness: float = 0.00
	receptionPerfects: int = 0
	receptionNeutrals: int = 0
	receptionErrors: int = 0
	totalReceptions: int = 0
	receptionEffectiveness: float = 0.00
	setPerfects: int = 0
	setNeutrals: int = 0
	setErrors: int = 0
	totalSets: int = 0
	setEffectiveness: float = 0.00
	totalPoints: int = 0
	totalPerfects: int = 0
	totalNeutrals: int = 0
	totalErrors: int = 0
	totalActions: int = 0
	totalEffectiveness: float = 0.00
	playerCreationDateTime: datetime = datetime.now()
	teams: list[Team] = []
	totalTeams: int = 0
	
	@validator("password")
	def passwordValidation(cls, v):
		return passwordCheck(v)

class Player(PlayerBase):
	totalGames = 0
	attackPoints: int = 0
	attackNeutrals: int = 0
	attackErrors: int = 0
	totalAttacks: int = 0
	attackEffectiveness: float = 0.00
	blockPoints: int = 0
	blockNeutrals: int = 0
	blockErrors: int = 0
	totalBlocks: int = 0
	blockEffectiveness: float = 0.00
	servicePoints: int = 0
	serviceNeutrals:int = 0
	serviceErrors: int = 0
	totalServices: int = 0
	serviceEffectiveness: float = 0.00
	defensePerfects: int = 0
	defenseNeutrals: int = 0
	defenseErrors: int = 0
	totalDefenses: int = 0
	defenseEffectiveness: float = 0.00
	receptionPerfects: int = 0
	receptionNeutrals: int = 0
	receptionErrors: int = 0
	totalReceptions: int = 0
	receptionEffectiveness: float = 0.00
	setPerfects: int = 0
	setNeutrals: int = 0
	setErrors: int = 0
	totalSets: int = 0
	setEffectiveness: float = 0.00
	totalPoints: int = 0
	totalPerfects: int = 0
	totalNeutrals: int = 0
	totalErrors: int = 0
	totalActions: int = 0
	totalEffectiveness: float = 0.00
	playerCreationDateTime: datetime = datetime.now()
	teams: list[Team] = []
	totalTeams: int = 0

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