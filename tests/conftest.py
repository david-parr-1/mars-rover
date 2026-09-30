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
