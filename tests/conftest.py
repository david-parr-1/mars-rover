import pytest

from src.classes import Plateau, Position, Rover
from src.custom_enums import CompassDirection


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
    rover = Rover(Position(1, 2, CompassDirection.NORTH), "LMR")

    return rover
