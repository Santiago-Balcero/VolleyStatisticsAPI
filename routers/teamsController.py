from fastapi import APIRouter, status, Depends
from routers.loginController import getCurrentPlayer
from models.teamModels import Team, UpdatedTeam
from utils import exceptions as ex
import services.teamsService as TeamService
from config.logger.logger import LOG

router = APIRouter(prefix = "/teams", tags = ["Teams"])

# Currently does not depend on AUTH through Depends(getCurrentPlayer) 
# because this is meant to be an ADMIN endpoint
@router.get("", status_code = status.HTTP_200_OK, response_model = list[Team])
async def getAllTeams():
	LOG.info("Request for getAllTeams.")
	teams: list[Team] = TeamService.getAllTeams()
	LOG.info("List of teams sent as response. Model: Team.")
	return teams

@router.get("/player", status_code = status.HTTP_200_OK, response_model = list[Team])
async def getTeamsByPlayer(playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for getTeamsByPlayer.")
	LOG.debug(f"User: {playerId}.")
	teams: list[Team] = TeamService.getTeamsByPlayer(playerId)
	LOG.info("List of teams sent as response. Model: Team.")
	return teams
 
@router.get("/{teamId}", status_code = status.HTTP_200_OK, response_model = Team)
async def getTeamById(teamId: str, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for getTeamById.")
	LOG.debug(f"User: {playerId}. Team: {teamId}.")
	team: Team = TeamService.getTeamById(teamId)
	LOG.info("Team info sent as response. Model: Team.")
	return team

@router.post("/newTeam", status_code = status.HTTP_201_CREATED, response_model = str)
async def createTeam(newTeam: Team, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for createTeam.")
	LOG.debug(f"User: {playerId}.")
	TeamService.createTeam(newTeam, playerId)
	LOG.info("New team created, response sent.")
	LOG.debug(f"New team: {newTeam.teamId}.") 
	return f"Team {newTeam.teamName} successfully registered."

@router.put("", status_code = status.HTTP_200_OK, response_model = str)
async def updateTeamName(updatedTeam: UpdatedTeam, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for updateTeamName.")
	LOG.debug(f"User: {playerId}. Team: {updatedTeam.teamId}")
	TeamService.updateTeamName(updatedTeam, playerId)
	LOG.info("Team updated, response sent.")
	return f"Team changed it's name to {updatedTeam.newTeamName}."
				
@router.delete("/{teamId}", status_code = status.HTTP_200_OK, response_model = str)
async def deleteTeam(teamId: str, playerId: str = Depends(getCurrentPlayer)):
	LOG.info("Request for deleteTeam.")
	LOG.debug(f"User: {playerId}. Team: {teamId}")
	TeamService.deleteTeam(teamId, playerId)
	LOG.info("Team deleted, response sent.")
	return "Team successfully deleted."

def checkTeamExistance(teams: list, teamName: str):
	# Checks if user has another registered team under the same new name
	# If so, raises exception
	for team in teams:
		if team["teamName"] == teamName:
			ex.teamAlreadyExists()
   