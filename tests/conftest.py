import pytest

from src.classes import Plateau


@pytest.fixture()
def plateau_class_instance():
    plateau = Plateau(1, 2)

    return plateau
