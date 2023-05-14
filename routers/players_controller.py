from fastapi import APIRouter, status, Depends
from routers.login_controller import get_current_player
from models.player_models import NewPlayer, Player, PlayerBase, NewPassword
from models.response_models import ResponseModel
import services.players_service as PlayerService
from config.logger.logger import LOG


router = APIRouter(prefix="/players", tags=["Players"])


# Currently does not depend on AUTH through Depends(get_current_player)
# because this is meant to be an ADMIN endpoint
@router.get("", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_all_players():
    LOG.info("Request for get_all_players.")
    players: list[Player] = PlayerService.get_all_players()
    LOG.info("List of players sent as response. Model: Player.")
    return ResponseModel(data=players)


@router.get("/player", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_player_by_id(player_id: str = Depends(get_current_player)):
    LOG.info("Request for get_player_by_id.")
    LOG.debug(f"User: {player_id}.")
    player: Player = PlayerService.get_player_by_id(player_id)
    LOG.info("Player info sent as response. Model: Player.")
    return ResponseModel(data=player)


# Does not depend on AUTH through Depends(get_current_player) because 
# this is used for creating new account
@router.post("", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def create_player(player: NewPlayer):
    LOG.info("Request for create_player.")    
    new_player_id: str = PlayerService.create_player(player)
    LOG.info("New player created, response sent.")
    LOG.debug(f"New user: {new_player_id}.")
    return ResponseModel(
        detail=f"Player {player.first_name} {player.last_name} successfully registered.")


@router.put("/password", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def update_password(new_password: NewPassword, player_id: str = Depends(get_current_player)):
    LOG.info("Request for update_password.")
    LOG.debug(f"User: {player_id}.")
    PlayerService.update_password(new_password, player_id)
    LOG.info("Password updated, response sent.")
    return ResponseModel(detail="Password successfully changed.")


@router.put("", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def update_player(player: PlayerBase, player_id: str = Depends(get_current_player)):
    LOG.info("Request for update_player.")
    LOG.debug(f"User: {player_id}.")
    PlayerService.update_player(player, player_id)
    LOG.info("Player updated, response sent.")
    return ResponseModel(detail="Player successfully updated.")


@router.delete("/delete", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def delete_player(player_id: str = Depends(get_current_player)):
    LOG.info("Request for delete_player.")
    LOG.debug(f"User: {player_id}.")
    PlayerService.delete_player(player_id)
    LOG.info("Player deleted, response sent.")
    return ResponseModel(detail="Player successfully deleted.")
