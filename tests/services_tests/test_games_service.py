import pytest
import sys
from decouple import config

sys.path.append(config("PROJECT_PATH"))

from services.games_service import valid_action_and_action_result


@pytest.mark.parametrize(
    "action, action_result, expected",
    [
        ("attack", "perfect", False),
        ("block", "perfect", False),
        ("defense", "point", False),
        ("service", "point", True),
        ("attack", "point", True),
        ("reception", "perfect", True)
    ])
def test_check_for_valid_action_and_action_result(action: str, action_result: str, expected):
    result = valid_action_and_action_result(action, action_result)
    assert result == expected
