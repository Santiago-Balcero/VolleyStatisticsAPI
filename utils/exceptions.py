from fastapi import HTTPException, status
from models.gameModels import Game
from config.logger.logger import LOG

def wrongCredentials() -> Exception:
	LOG.warning("Wrong credentials error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Wrong login credentials.")

def invalidToken() -> Exception:
    LOG.warning("Invalid token response sent.")
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid token.")

def playerAlreadyExists() -> Exception:
	LOG.warning("Player already registered in database error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Player already registered in database.")

def playerNotFound() -> Exception:
	LOG.warning("Player not found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Player not found.")

def noPlayersFound() -> Exception:
	LOG.warning("No players found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No players found.")

def unableToCreatePlayer() -> Exception:
	LOG.warning("Unable to create player error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create player.")

def invalidPassword() -> Exception:
	LOG.warning("Invalid password error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid password.")

def unableToUpdatePassword() -> Exception:
    LOG.warning("Unable to update password response sent.")
    raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to update password.")

def unableToUpdatePlayer() -> Exception:
	LOG.warning("Unable to update player error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to update player.")

def teamAlreadyExists() -> Exception:
	LOG.warning("Team already registered in player's database error response sent.")  
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Team already registered in player's database.")

def teamNotFound() -> Exception:
	LOG.warning("Team not found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Team not found.")

def noTeamsFound() -> Exception:
	LOG.warning("No teams found error response sent.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No teams found.")

def unableToCreateTeam() -> Exception:
	LOG.warning("Unable to create team error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create team.")

def activeGame(game: Game) -> Exception:
	LOG.debug(f"Active game: id {game['gameId']}, started at {game['gameDateTime']}, vs {game['opponentTeam']}")
	LOG.warning("There is another active game error response sent.")
	raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"There is another active game: game with id {game['gameId']} started at {game['gameDateTime']} in {game['gameCity']}, {game['gameCountry']} vs {game['opponentTeam']} is still active.")

def gameNotFound() -> Exception:
	LOG.warning("Game not found.")
	raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Game not found.")

def gameAlreadyFinished() -> Exception:
	LOG.warning("Game was already finished error response sent.")
	raise HTTPException(status_code = status.HTTP_405_METHOD_NOT_ALLOWED, detail = "Game was already finished.")

def unableToCreateGame() -> Exception:
	LOG.warning("Unable to create game error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create game.")

def unableToUpdateGame() -> Exception:
	LOG.warning("Unable to update game error response sent.")
	raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to update game.")

def invalidAction() -> Exception:
	LOG.warning("Invalid action error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid action.")

def invalidActionResult() -> Exception:
	LOG.warning("Invalid action result error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid action result.")

def invalidActionAndActionResult() -> Exception:
	LOG.warning("Invalid combination for action and action result error response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid combination for action and action result.")

def invalidObjectId() -> Exception:
	LOG.warning("Invalid ObjectId response sent.")
	raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid ObjectId.")

def noDataConnection(e: str) -> Exception:
    LOG.warning(f"No connection with database. Error: -> {e}")
    raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "No connection with database.")
