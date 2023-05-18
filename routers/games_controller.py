from fastapi import APIRouter, status, Depends
from routers.login_controller import get_current_player
from models.game_models import Game, GameAction, EndGame
from models.response_models import ResponseModel
import services.games_service as GameService
from config.logger.logger import LOG


router = APIRouter(prefix="/games", tags=["Games"])


@router.get("/{game_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_game_by_id(game_id: str, player_id: str = Depends(get_current_player)):
    LOG.info("Request for get_game_by_id.")
    LOG.debug(f"User: {player_id}. Game: {game_id}.")
    game: Game = GameService.get_game_by_id(game_id)
    LOG.info("Game info sent as response. Model: Game.")
    return ResponseModel(data=game)


@router.post("/{team_id}", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def create_game(team_id: str, new_game: Game, player_id: str = Depends(get_current_player)):
    LOG.info("Request for create_game.")
    LOG.debug(f"User: {player_id}. Team: {team_id}.")
    game: Game = GameService.create_game(team_id, new_game, player_id)
    LOG.info("New game created, response sent.")
    LOG.debug(f"New game: {new_game.game_id}")
    return ResponseModel(data=game, detail=f"Game {new_game.game_id} has started.")


@router.put("/finish_game", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def finish_game(game_to_finish: EndGame, player_id: str = Depends(get_current_player)):
    LOG.info("Request for finish_game.")
    LOG.debug(f"User: {player_id}. Team: {game_to_finish.team_id}. Game: {game_to_finish.game_id}.")
    GameService.finish_game(game_to_finish)
    LOG.info("Game finished , response sent.")
    return ResponseModel(detail=f"Game with id {game_to_finish.game_id} was finished.")
    

@router.put("/play_game", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def play_game(game_action: GameAction, player_id: str = Depends(get_current_player)):
    LOG.info("Request for play_game.")
    LOG.debug(f"User: {player_id}. Team: {game_action.team_id}. Game: {game_action.game_id}.")
    game: Game = GameService.play_game(game_action, player_id)
    LOG.info("Game updated, response sent. Model: Game.")
    return ResponseModel(data=game)
