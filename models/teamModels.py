from bson import ObjectId
from pydantic import BaseModel, validator
from models.gameModels import Game
from utils.constants import TEAM_CATEGORIES
from datetime import datetime

class Team(BaseModel):
	teamId: str = None
	teamName: str
	teamCategory: str
	games: list[Game] = []
	totalGames: int = 0
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
	teamCreationDateTime: datetime = datetime.now()
	
	@validator("teamName")
	def teamNameValidation(cls, v):
		return validateName(v)
	
	@validator("teamCategory")
	def teamCategoryValidation(cls, v):
		v = v.strip().title()
		if v not in TEAM_CATEGORIES:
			raise ValueError("Invalid team category.")
		return v			

class UpdatedTeam(BaseModel):
	teamId: str
	newTeamName: str

	@validator("teamId")
	def teamIdValidation(cls, v):
		if not ObjectId.is_valid(v):
			raise ValueError("Invalid team id.")
		return v

	@validator("newTeamName")
	def teamNameValidation(cls, v):
		return validateName(v)
	
def validateName(name: str) -> str:
	name = name.strip().title()
	if len(name) < 1:
		raise ValueError("Invalid team name.")
	return name