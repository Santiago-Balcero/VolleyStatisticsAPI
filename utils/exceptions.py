from fastapi import HTTPException, status
from models.gameModels import Game
from logging.config import dictConfig
import logging
from config.logger.loggerConfig import LogConfig

dictConfig(LogConfig().dict())
log = logging.getLogger("volleystats")

def wrongCredentials() -> Exception:
	log.warning("Wrong credentials error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Wrong login credentials.")

def invalidToken() -> Exception:
    log.warning("Invalid token response sent.")
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid token.")

def playerAlreadyExists() -> Exception:
	log.warning("Player already registered in database error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Player already registered in database.")

def playerNotFound() -> Exception:
	log.warning("Player not found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Player not found.")

def noPlayersFound() -> Exception:
	log.warning("No players found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No players found.")

def unableToCreatePlayer() -> Exception:
	log.warning("Unable to create player error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create player.")

def invalidPassword() -> Exception:
	log.warning("Invalid password error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid password.")

def unableToUpdatePlayer() -> Exception:
	log.warning("Unable to update player error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to update player.")

def teamAlreadyExists() -> Exception:
	log.warning("Team already registered in player's database error response sent.")  
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Team already registered in player's database.")

def teamNotFound() -> Exception:
	log.warning("Team not found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Team not found.")

def noTeamsFound() -> Exception:
	log.warning("No teams found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No teams found.")

def unableToCreateTeam() -> Exception:
	log.warning("Unable to create team error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create team.")

def activeGame(game: Game) -> Exception:
	log.debug(f"Active game: id {game['gameId']}, started at {game['gameDateTime']}, vs {game['opponentTeam']}")
	log.warning("There is another active game error response sent.")
	raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"There is another active game: game with id {game['gameId']} started at {game['gameDateTime']} in {game['gameCity']}, {game['gameCountry']} vs {game['opponentTeam']} is still active.")

def gameNotFound() -> Exception:
	log.warning("Game not found.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Game not found.")

def gameAlreadyFinished() -> Exception:
	log.warning("Game was already finished error response sent.")
	raise HTTPException(status_code = status.HTTP_405_METHOD_NOT_ALLOWED, detail = "Game was already finished.")

def unableToCreateGame() -> Exception:
	log.warning("Unable to create game error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create game.")

def unableToUpdateGame() -> Exception:
	log.warning("Unable to update game error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to update game.")

def invalidAction() -> Exception:
	log.warning("Invalid action error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid action.")

def invalidActionResult() -> Exception:
	log.warning("Invalid action result error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid action result.")

def invalidActionAndActionResult() -> Exception:
	log.warning("Invalid combination for action and action result error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid combination for action and action result.")

def invalidObjectId() -> Exception:
	log.warning("Invalid ObjectId response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid ObjectId.")
