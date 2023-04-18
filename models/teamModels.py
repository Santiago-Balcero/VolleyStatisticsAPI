from bson import ObjectId
from pydantic import BaseModel, validator
from models.gameModels import Game
from utils.constants import TEAM_CATEGORIES
from datetime import datetime

class NewTeam(BaseModel):
	teamName: str
	teamCategory: str
	
	@validator("teamName")
	def teamNameValidation(cls, v):
		return validateName(v)
	
	@validator("teamCategory")
	def teamCategoryValidation(cls, v):
		v = v.strip().title()
		if v not in TEAM_CATEGORIES:
			raise ValueError("Invalid team category.")
		return v
	
class Team(NewTeam):
	teamId: str
	games: list[Game]
	teamCreationDateTime: str
	
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
