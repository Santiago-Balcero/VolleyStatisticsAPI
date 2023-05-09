from fastapi import APIRouter, status, Depends
from routers.login_controller import get_current_player
from models.team_models import Team, UpdatedTeam
from models.response_models import ResponseModel
import services.teams_service as TeamService
from config.logger.logger import LOG


router = APIRouter(prefix="/teams", tags=["Teams"])


# Currently does not depend on AUTH through Depends(get_current_player)
# because this is meant to be an ADMIN endpoint
@router.get("", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_all_teams():
    LOG.info("Request for get_all_teams.")
    teams: list[Team] = TeamService.get_all_teams()
    LOG.info("List of teams sent as response. Model: Team.")
    return ResponseModel(data=teams)


@router.get("/player", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_teams_by_player(player_id: str = Depends(get_current_player)):
    LOG.info("Request for get_teams_by_player.")
    LOG.debug(f"User: {player_id}.")
    teams: list[Team] = TeamService.get_teams_by_player(player_id)
    LOG.info("List of teams sent as response. Model: Team.")
    return ResponseModel(data=teams)


@router.get("/{team_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def get_team_by_id(team_id: str, player_id: str = Depends(get_current_player)):
    LOG.info("Request for get_team_by_id.")
    LOG.debug(f"User: {player_id}. Team: {team_id}.")
    team: Team = TeamService.get_team_by_id(team_id)
    LOG.info("Team info sent as response. Model: Team.")
    return ResponseModel(data=team)


@router.post("/new_team", status_code=status.HTTP_201_CREATED, response_model=ResponseModel)
async def create_team(new_team: Team, player_id: str = Depends(get_current_player)):
    LOG.info("Request for create_team.")
    LOG.debug(f"User: {player_id}.")
    TeamService.create_team(new_team, player_id)
    LOG.info("New team created, response sent.")
    LOG.debug(f"New team: {new_team.team_id}.") 
    return ResponseModel(detail=f"Team {new_team.team_name} successfully registered.")


@router.put("", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def update_team_name(updated_team: UpdatedTeam, player_id: str = Depends(get_current_player)):
    LOG.info("Request for updateteam_name.")
    LOG.debug(f"User: {player_id}. Team: {updated_team.team_id}")
    TeamService.update_team_name(updated_team)
    LOG.info("Team updated, response sent.")
    return ResponseModel(detail=f"Team changed it's name to {updated_team.new_team_name}.")


@router.delete("/{team_id}", status_code=status.HTTP_200_OK, response_model=ResponseModel)
async def delete_team(team_id: str, player_id: str = Depends(get_current_player)):
    LOG.info("Request for delete_team.")
    LOG.debug(f"User: {player_id}. Team: {team_id}")
    TeamService.delete_team(team_id, player_id)
    LOG.info("Team deleted, response sent.")
    return ResponseModel(detail="Team successfully deleted.")
