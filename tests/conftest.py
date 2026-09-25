import pytest

from src.classes import Plateau, Position, Rover
from src.custom_enums import CompassDirection, Instruction, RoverType


@pytest.fixture()
def plateau_class_instance():
    plateau = Plateau(1, 2)

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
