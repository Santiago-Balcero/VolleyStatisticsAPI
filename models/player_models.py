from datetime import datetime
from pydantic import BaseModel, validator
from models.team_models import Team
from utils.constants import PLAYER_POSITIONS, PLAYER_CATEGORIES
from utils import exceptions as ex
import re


class PlayerBase(BaseModel):
    first_name: str
    last_name: str
    category: str  # Category on which player plays Men or Women
    position: str
    email: str

    @validator("first_name")
    def first_name_validation(cls, val):
        val = val.strip().title()
        if len(val) < 1 or len(val) > 30:
            ex.invalid_value("first name")
        return val

    @validator("last_name")
    def last_name_validation(cls, val):
        val = val.strip().title()
        if len(val) < 1 or len(val) > 30:
            ex.invalid_value("last name")
        return val

    @validator("category")
    def category_validation(cls, val):
        val = val.strip().title()
        if val not in PLAYER_CATEGORIES:
            ex.invalid_value("category")
        return val

    @validator("position")
    def position_validation(cls, val):
        val = val.strip().upper()
        # OH = Outside Hitter, S = Setter, MB = Middle Blocker, L = Libero, O = Opposite spiker
        if val not in PLAYER_POSITIONS:
            ex.invalid_value("position")
        return val
    
    @validator("email")
    def email_validation(cls, val):
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'
        if not re.fullmatch(regex, val):
            ex.invalid_value("email")
        return val


class NewPlayer(PlayerBase):
    password: str
    total_games = 0
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
    player_creation_date_time: datetime = datetime.now()
    teams: list[Team] = []
    total_teams: int = 0

    @validator("password")
    def password_validation(cls, val):
        return password_check(val)


class Player(PlayerBase):
    total_games = 0
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
    player_creation_date_time: datetime = datetime.now()
    teams: list[Team] = []
    total_teams: int = 0


class LoginPlayer(BaseModel):
    player_id: str
    email: str
    password: str


class NewPassword(BaseModel):
    new_password: str

    @validator("new_password")
    def password_validation(cls, val):
        return password_check(val)


def password_check(val):
    val = val.strip()
    if " " in val or len(val) < 12 or sum(1 for x in val if x.isupper()) == 0 or \
            sum(1 for x in val if x.islower()) == 0 or sum(1 for x in val if x.isdigit()) == 0:
        ex.invalid_value("password")
    return val
