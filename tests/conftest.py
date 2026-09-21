import pytest

from src.classes import Plateau, Position
from src.custom_enums import CompassDirection


@pytest.fixture()
def plateau_class_instance():
    plateau = Plateau(1, 2)

    return plateau


@pytest.fixture
def position_class_instance():
    position = Position(1, 2, CompassDirection.NORTH)

    return position
