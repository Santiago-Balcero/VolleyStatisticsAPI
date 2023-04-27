from pydantic import BaseModel, validator
from datetime import datetime
from utils.constants import ACTION_RESULTS, GAME_ACTIONS, GAME_POSITIONS
from utils import exceptions as ex
from bson import ObjectId

class Game(BaseModel):
	gameId: str = ObjectId()
	gameDateTime: datetime = datetime.now()
	status: int = 1 # 1 for active game, 0 for finished game
	gameCountry: str
	gameCity: str
	opponentTeam: str # value: "Random" for when is non serious game
	playerPosition: str # ANY for when is non serious game
	playerNumber: str # ANY for when is non serious game
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
	totalActions: int = 0
	totalPoints: int = 0
	totalPerfects: int = 0
	totalNeutrals: int = 0
	totalErrors: int = 0
	totalEffectiveness: float = 0.00
	
	@validator("gameCountry")
	def gameCountryValidation(cls, v):
		v = v.strip().title()
		if len(v) < 4:
			raise ValueError("Invalid country name.")
		return v
	
	@validator("gameCity")
	def gameCityValidation(cls, v):
		v = v.strip().title()
		if len(v) < 1:
			raise ValueError("Invalid city name.")
		return v
	
	@validator("opponentTeam")
	def opponentTeamValidation(cls, v):
		v = v.strip().title()
		if len(v) < 1:
			raise ValueError("Invalid opponent team name.")
		return v
		
	@validator("playerPosition")
	def playerPositionValidation(cls, v):
		v = v.strip().upper()
		if v not in GAME_POSITIONS:
			raise ValueError("Invalid position.")
		return v
	
	@validator("playerNumber")
	def playerNumberValidation(cls, v):
		v = v.strip().upper()
		if not v == "ANY" and not v.isdigit():
			raise ValueError("Invalid player number.")
		return v

class EndGame(BaseModel):
	teamId: str
	gameId: str
 
	@validator("teamId")
	def teamIdValidation(cls, v):
		if not ObjectId.is_valid(v):
			ex.invalidObjectId("team")
		return v

	@validator("gameId")
	def gameIdValidation(cls, v):
		if not ObjectId.is_valid(v):
			ex.invalidObjectId("game")
		return v

class GameAction(EndGame):
	action: str
	actionResult: str
  
	@validator("action")
	def actionValidation(cls, v):
		action = v.strip().lower()
		if not action in GAME_ACTIONS:
			ex.invalidAction()
		return action
	
	@validator("actionResult")
	def actionResultValidation(cls, v):
		result = v.strip()
		if not result in ACTION_RESULTS:
			ex.invalidActionResult()
		# Returns as title() and adding a final "s" because attributes names are for example "attackPoints"
		return f"{result.title()}s"