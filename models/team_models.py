from datetime import datetime
from bson import ObjectId
from pydantic import BaseModel, validator
from utils.constants import TEAM_CATEGORIES
from models.game_models import Game


class Team(BaseModel):
    team_id: str = ""
    team_name: str
    team_category: str
    games: list[Game] = []
    total_games: int = 0
    attack_points: int = 0
    attack_neutrals: int = 0
    attack_errors: int = 0
    total_attacks: int = 0
    attack_effectiveness: float = 0.00
    block_points: int = 0
    block_neutrals: int = 0
    block_errors: int = 0
    total_blocks: int = 0
    block_effectiveness: float = 0.00
    service_points: int = 0
    service_neutrals: int = 0
    service_errors: int = 0
    total_services: int = 0
    service_effectiveness: float = 0.00
    defense_perfects: int = 0
    defense_neutrals: int = 0
    defense_errors: int = 0
    total_defenses: int = 0
    defense_effectiveness: float = 0.00
    reception_perfects: int = 0
    reception_neutrals: int = 0
    reception_errors: int = 0
    total_receptions: int = 0
    reception_effectiveness: float = 0.00
    set_perfects: int = 0
    set_neutrals: int = 0
    set_errors: int = 0
    total_sets: int = 0
    set_effectiveness: float = 0.00
    total_points: int = 0
    total_perfects: int = 0
    total_neutrals: int = 0
    total_errors: int = 0
    total_actions: int = 0
    total_effectiveness: float = 0.00
    team_creation_date_time: datetime = datetime.now()

    @validator("team_name")
    def team_name_validation(cls, val):
        return validate_name(val)

    @validator("team_category")
    def team_category_validation(cls, val):
        val = val.strip().title()
        if val not in TEAM_CATEGORIES:
            raise ValueError("Invalid team category.")
        return val


class UpdatedTeam(BaseModel):
    team_id: str
    new_team_name: str

    @validator("team_id")
    def team_id_validation(cls, val):
        if not ObjectId.is_valid(val):
            raise ValueError("Invalid team id.")
        return val

    @validator("new_team_name")
    def team_name_validation(cls, val):
        return validate_name(val)


def validate_name(name: str) -> str:
    name = name.strip().title()
    if len(name) < 1:
        raise ValueError("Invalid team name.")
    return name
