from datetime import datetime
from pydantic import BaseModel, validator
from bson import ObjectId
from utils.constants import ACTION_RESULTS, GAME_ACTIONS, GAME_POSITIONS


class Game(BaseModel):
    game_id: str = ""
    game_date_time: datetime = datetime.now()
    status: int = 1  # 1 for active game, 0 for finished game
    game_country: str
    game_city: str
    opponent_team: str  # value: "Random" for when is non serious game
    player_position: str  # ANY for when is non serious game
    player_number: str  # ANY for when is non serious game
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

    @validator("game_country")
    def game_country_validation(cls, val):
        val = val.strip().title()
        if len(val) < 4:
            raise ValueError("Invalid country name.")
        return val

    @validator("game_city")
    def game_city_validation(cls, val):
        val = val.strip().title()
        if len(val) < 1:
            raise ValueError("Invalid city name.")
        return val

    @validator("opponent_team")
    def opponent_team_validation(cls, val):
        val = val.strip().title()
        if len(val) < 1:
            raise ValueError("Invalid opponent team name.")
        return val

    @validator("player_position")
    def player_position_validation(cls, val):
        val = val.strip().upper()
        if val not in GAME_POSITIONS:
            raise ValueError("Invalid position.")
        return val

    @validator("player_number")
    def player_number_validation(cls, val):
        val = val.strip().upper()
        if not val == "ANY" and not val.isdigit():
            raise ValueError("Invalid player number.")
        return val


class EndGame(BaseModel):
    team_id: str
    game_id: str

    @validator("team_id")
    def team_id_validation(cls, val):
        if not ObjectId.is_valid(val):
            raise ValueError("Invalid team id.")
        return val

    @validator("game_id")
    def game_id_validation(cls, val):
        if not ObjectId.is_valid(val):
            raise ValueError("Invalid game id.")
        return val


class GameAction(EndGame):
    action: str
    action_result: str

    @validator("action")
    def action_validation(cls, val):
        action = val.strip().lower()
        if action not in GAME_ACTIONS:
            raise ValueError("Invalid action.")
        return action

    @validator("action_result")
    def action_result_validation(cls, val):
        result = val.strip()
        if result not in ACTION_RESULTS:
            raise ValueError("Invalid action result.")
        # Returns as title() and adding a final "s" because
        # attributes names are for example "attackPoints"
        return f"{result}s"
