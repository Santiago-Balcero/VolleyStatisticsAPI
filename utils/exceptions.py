from fastapi import HTTPException, status
from db.models.game import Game

def playerAlreadyExists() -> Exception:
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Player already registered in database.")

def playerNotFound() -> Exception:
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Player not found.")

def noPlayersFound() -> Exception:
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No players found.")

def unableToCreatePlayer() -> Exception:
    raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create player.")

def unableToUpdatePlayer() -> Exception:
    raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to update player.")

def teamAlreadyExists() -> Exception:
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Team already registered in player's database.")

def teamNotFound() -> Exception:
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Team not found.")

def noTeamsFound() -> Exception:
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "No teams found.")

def unableToCreateTeam() -> Exception:
    raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to create team.")

def activeGame(game: Game) -> Exception:
    raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail = f"Game {game['gameId']} started at {game['gameDateTime']} in {game['gameCity']}, {game['gameCountry']} vs {game['opponentTeam']} is still active.")

def gameNotFound() -> Exception:
    raise HTTPException(status_code = status.HTTP_404_NOT_FOUND, detail = "Game not found.")

def gameAlreadyFinished() -> Exception:
    raise HTTPException(status_code = status.HTTP_405_METHOD_NOT_ALLOWED, detail = "Game was already finished.")

def unableToUpdateGame() -> Exception:
    raise HTTPException(status_code = status.HTTP_500_INTERNAL_SERVER_ERROR, detail = "Unable to update game.")

def invalidAction() -> Exception:
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid action.")

def invalidActionResult() -> Exception:
    raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = "Invalid action result.")