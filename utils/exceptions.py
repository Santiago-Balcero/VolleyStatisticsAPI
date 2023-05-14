from fastapi import HTTPException, status
from config.logger.logger import LOG


def wrong_credentials() -> Exception:
    LOG.warning("Wrong credentials error response sent.")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Wrong login credentials.")


def invalid_token() -> Exception:
    LOG.warning("Invalid token response sent.")
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid token.")


def player_already_exists() -> Exception:
    LOG.warning("Player already registered in database error response sent.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Player already registered in database.")


def player_not_found() -> Exception:
    LOG.warning("Player not found error response sent.")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Player not found.")


def unable_to_create_player() -> Exception:
    LOG.warning("Unable to create player error response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to create player.")


def unable_to_update_password() -> Exception:
    LOG.warning("Unable to update password response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to update password.")


def unable_to_update_player() -> Exception:
    LOG.warning("Unable to update player error response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to update player.")


def team_already_exists() -> Exception:
    LOG.warning(
        "Team already registered in player's database error response sent.")  
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Team already registered in player's database.")


def team_not_found() -> Exception:
    LOG.warning("Team not found error response sent.")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Team not found.")


def unable_to_create_team() -> Exception:
    LOG.warning("Unable to create team error response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to create team.")


def active_game(game) -> Exception:
    LOG.debug(f"Active game: id {game.game_id}, started at {game.game_date_time}, \
        vs {game.opponent_team}.")
    LOG.warning("There is another active game error response sent.")
    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                        detail=f"There is another active game. Game with id {game.game_id}," +
                        f" started at {game.game_date_time} in {game.game_city}," +
                        f" {game.game_country}, vs {game.opponent_team}, is still active.")


def game_not_found() -> Exception:
    LOG.warning("Game not found response sent.")
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="Game not found.")


def game_already_finished() -> Exception:
    LOG.warning("Game was already finished error response sent.")
    raise HTTPException(status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
                        detail="Game was already finished.")


def unable_to_create_game() -> Exception:
    LOG.warning("Unable to create game error response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to create game.")


def unable_to_update_game() -> Exception:
    LOG.warning("Unable to update game error response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to update game.")


def invalid_action() -> Exception:
    LOG.warning("Invalid action error response sent.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid action.")


def invalid_action_result() -> Exception:
    LOG.warning("Invalid action result error response sent.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid action result.")


def invalid_action_and_action_result() -> Exception:
    LOG.warning("Invalid combination for action and action result error response sent.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid combination for action and action result.")


def invalid_object_id(obj: str) -> Exception:
    LOG.warning("Invalid ObjectId response sent.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, 
                        detail=f"Invalid ObjectId. Object: {obj}.")


def no_data_connection(method: str, e: Exception) -> Exception:
    LOG.warning(f"No connection with database. Method: {method}. Error: -> {e}")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="No connection with database.")


def unable_to_delete_player() -> Exception:
    LOG.warning("Unable to delete player response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to delete player.")


def unable_to_update_team() -> Exception:
    LOG.warning("Unable to update team error response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to update team.")


def unable_to_delete_team() -> Exception:
    LOG.warning("Unable to delete team response sent.")
    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        detail="Unable to delete team.")


def invalid_value(value: str) -> Exception:
    LOG.warning(f"Invalid value for {value} response sent.")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid value for {value}.")
