import os
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from main import execute_mission


@pytest.fixture()
def dummy_mission_1():
    return "5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM"


@pytest.fixture()
def dummy_mission_2():
    return "8 8\n3 4 S\nMLMMMLMMMRM\n5 6 W\nMMLMRMM\n8 1 N\nMLMMMRMMR"


@pytest.fixture()
def dummy_mission_with_rover_types():
    return "8 8\n3 4 S\nMLMMMLMMMRM\n5 6 W\nMMLMRMM\n8 1 N\nMLMMMRMMR\n5 5 N C\nMRMRML"


def test_execute_dummy_mission_1_returns_correct_output(
    dummy_mission_1, temp_directory
):
    expected_result = "1 3 N S\n5 1 E S"

    result = execute_mission(dummy_mission_1, temp_directory)

    assert result == expected_result


def test_execute_dummy_mission_2_returns_correct_output(
    dummy_mission_2, temp_directory
):
    expected_result = "7 6 E S\n1 5 W S\n5 4 E S"

    result = execute_mission(dummy_mission_2, temp_directory)

    assert result == expected_result


def test_execute_dummy_mission_with_rover_type_returns_correct_output(
    dummy_mission_with_rover_types, temp_directory
):
    expected_result = "7 6 E S\n1 5 W S\n5 4 E S\n7 5 E C"

    result = execute_mission(dummy_mission_with_rover_types, temp_directory)

    assert result == expected_result


@patch("main.datetime")
def test_execute_dummy_mission_writes_to_archive(
    mocked_datetime,
    temp_directory,
    dummy_mission_with_rover_types,
):
    fixed_timestamp = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
    mocked_datetime.now.return_value = fixed_timestamp
    expected_archive_filename = (
        f"mission_archive_{fixed_timestamp.strftime('%Y-%m-%d %H_%M_%S')}.json"
    )
    expected_archive_path = temp_directory / expected_archive_filename

    execute_mission(dummy_mission_with_rover_types, temp_directory)

    assert os.path.exists(expected_archive_path)
