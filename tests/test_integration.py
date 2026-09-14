import pytest

from main import execute_mission


@pytest.fixture()
def dummy_mission_1():
    return "5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM"


@pytest.fixture()
def dummy_mission_2():
    return "8 8\n3 4 S\nMLMMMLMMMRM\n5 6 W\nMMLMRMM\n8 1 N\nMLMMMRMMR"


def test_execute_dummy_mission_1_returns_correct_output(dummy_mission_1):
    expected_result = "1 3 N\n5 1 E"

    result = execute_mission(dummy_mission_1)

    assert result == expected_result


def test_execute_dummy_mission_2_returns_correct_output(dummy_mission_2):
    expected_result = "7 6 E\n1 5 W\n5 4 E"

    result = execute_mission(dummy_mission_2)

    assert result == expected_result
