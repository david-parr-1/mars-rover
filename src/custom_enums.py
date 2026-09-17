from enum import Enum


class Instruction(Enum):
    LEFT = "L"
    RIGHT = "R"
    MOVE = "M"


class CompassDirection(Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"
