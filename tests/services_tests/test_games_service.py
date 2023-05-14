import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from services.games_service import valid_action_and_action_result


@pytest.mark.parametrize(
    "action, action_result, expected",
    [
        ("attack", "perfects", False),
        ("block", "perfects", False),
        ("defense", "points", False),
        ("service", "points", True),
        ("attack", "points", True),
        ("reception", "perfects", True)
    ])
def test_check_for_valid_action_and_action_result(action: str, action_result: str, expected):
    result = valid_action_and_action_result(action, action_result)
    assert result == expected
