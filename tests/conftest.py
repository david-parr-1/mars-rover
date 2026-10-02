from datetime import datetime, timezone

import pytest

from src.classes import Mission, Plateau, Position, Rover
from src.custom_enums import CompassDirection, Instruction, RoverType


@pytest.fixture()
def plateau_class_instance():
    plateau = Plateau(1, 2)

    return plateau


@pytest.fixture
def eight_by_eight_plateau_instance():
    plateau = Plateau(8, 8)

    return plateau


@pytest.fixture
def position_class_instance():
    position = Position(1, 2, CompassDirection.NORTH)

    return position


@pytest.fixture
def rover_class_instance():
    plateau = Plateau(5, 5)
    rover = Rover(Position(1, 2, CompassDirection.NORTH), "LMR", plateau)

    return rover


@pytest.fixture
def rover_class_instance_with_list_of_instructions():
    plateau = Plateau(5, 5)
    rover = Rover(
        Position(1, 2, CompassDirection.NORTH),
        [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT],
        plateau,
    )

    return rover


@pytest.fixture
def rover_class_instance_with_latest_position_arg():
    plateau = Plateau(5, 5)
    rover = Rover(
        Position(1, 2, CompassDirection.NORTH),
        [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT],
        plateau,
        latest_position=Position(3, 4, CompassDirection.EAST),
    )

    return rover


@pytest.fixture
def rover_as_dict():
    return {
        "start_position": {"x": 1, "y": 2, "direction": "N"},
        "latest_position": {"x": 3, "y": 4, "direction": "E"},
        "instructions": "LMR",
        "rover_type": "S",
    }


@pytest.fixture
def cargo_rover_class_instance():
    plateau = Plateau(5, 5)
    rover = Rover(
        Position(1, 2, CompassDirection.NORTH),
        [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT],
        plateau,
        RoverType.CARGO,
    )

    return rover


@pytest.fixture
def mission_instance(
    eight_by_eight_plateau_instance,
    rover_class_instance_with_list_of_instructions,
    cargo_rover_class_instance,
):
    mission = Mission(
        eight_by_eight_plateau_instance,
        [rover_class_instance_with_list_of_instructions, cargo_rover_class_instance],
        datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )

    return mission


@pytest.fixture
def mission_instance_identical(
    eight_by_eight_plateau_instance,
    rover_class_instance_with_list_of_instructions,
    cargo_rover_class_instance,
):
    mission = Mission(
        eight_by_eight_plateau_instance,
        [rover_class_instance_with_list_of_instructions, cargo_rover_class_instance],
        datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )

    return mission


@pytest.fixture
def mission_instance_different_plateau(
    rover_class_instance_with_list_of_instructions,
    cargo_rover_class_instance,
):
    mission = Mission(
        Plateau(10, 10),
        [rover_class_instance_with_list_of_instructions, cargo_rover_class_instance],
        datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )

    return mission


@pytest.fixture
def mission_instance_different_rovers(
    eight_by_eight_plateau_instance,
    rover_class_instance_with_list_of_instructions,
):
    mission = Mission(
        eight_by_eight_plateau_instance,
        [rover_class_instance_with_list_of_instructions],
        datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )

    return mission


@pytest.fixture
def mission_instance_different_timestamp(
    eight_by_eight_plateau_instance,
    rover_class_instance_with_list_of_instructions,
    cargo_rover_class_instance,
):
    mission = Mission(
        eight_by_eight_plateau_instance,
        [rover_class_instance_with_list_of_instructions, cargo_rover_class_instance],
        datetime(2026, 1, 2, 12, 0, 0, tzinfo=timezone.utc),
    )

    return mission


@pytest.fixture
def mission_as_dict():
    mission = {
        "plateau": {"max_x": 8, "max_y": 8},
        "rovers": [
            {
                "start_position": {"x": 1, "y": 2, "direction": "N"},
                "latest_position": {"x": 3, "y": 4, "direction": "E"},
                "instructions": "LMR",
                "rover_type": "S",
            },
            {
                "start_position": {"x": 5, "y": 6, "direction": "S"},
                "latest_position": {"x": 7, "y": 8, "direction": "W"},
                "instructions": "RML",
                "rover_type": "C",
            },
        ],
        "timestamp": "2026-01-01T12:00:00+00:00",
    }

    return mission


@pytest.fixture
def mission_as_dict_no_plateau():
    mission = {
        "rovers": [
            {
                "start_position": {"x": 1, "y": 2, "direction": "N"},
                "latest_position": {"x": 3, "y": 4, "direction": "E"},
                "instructions": "LMR",
                "rover_type": "S",
            },
            {
                "start_position": {"x": 5, "y": 6, "direction": "S"},
                "latest_position": {"x": 7, "y": 8, "direction": "W"},
                "instructions": "RML",
                "rover_type": "C",
            },
        ],
        "timestamp": "2026-01-01T12:00:00+00:00",
    }

    return mission


@pytest.fixture
def mission_as_dict_no_rovers():
    mission = {
        "plateau": {"max_x": 8, "max_y": 8},
        "timestamp": "2026-01-01T12:00:00+00:00",
    }

    return mission


@pytest.fixture
def mission_as_dict_no_timestamp():
    mission = {
        "plateau": {"max_x": 8, "max_y": 8},
        "rovers": [
            {
                "start_position": {"x": 1, "y": 2, "direction": "N"},
                "latest_position": {"x": 3, "y": 4, "direction": "E"},
                "instructions": "LMR",
                "rover_type": "S",
            },
            {
                "start_position": {"x": 5, "y": 6, "direction": "S"},
                "latest_position": {"x": 7, "y": 8, "direction": "W"},
                "instructions": "RML",
                "rover_type": "C",
            },
        ],
    }

    return mission
