import inspect
import re
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from src.custom_enums import CompassDirection, Instruction
from src.exceptions import (
    InvalidInstructionError,
    InvalidPlateauError,
    InvalidPositionError,
)
from src.logging_config import get_logger

logger = get_logger(__name__)


def argument_type_validator(
    argument_types: dict[str, type],
) -> Callable[..., Callable[..., Any]]:
    """
    A decorator function that inspects the data types of the arguments passed to the
    wrapped function and raises a TypeError exception if they do not match. If the
    wrapped function's input argument match their expected data types then the wrapped
    function is executed and its output returned.

    Args:
        `argument_types`: A dictionary where each key is one of the wrapped function's
        arguments and its value is the object type that that argument should be. e.g.:
        ```python
        {"name": str, "count": int}
        ```
    Returns:
        The result of the executed wrapped function
    Raises:
        TypeError: If the data type of any argument passed to the wrapped function does
        not match the expected data type as defined in the `argument_types` dictionary.
    """

    def decorator(func) -> Callable[..., Any]:
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            for arg in bound_args.arguments:
                arg_value = bound_args.arguments[arg]
                if not isinstance(arg_value, argument_types[arg]):
                    logger.error(
                        f"Function {func.__name__} received invalid argument data "
                        f"type. Expected {argument_types[arg]} but got "
                        f"{type(arg_value)}"
                    )
                    raise TypeError(
                        f"Expected {argument_types[arg]} as type for {arg} argument "
                        f"but got {type(arg_value)}"
                    )
            return func(*args, **kwargs)

        return wrapper

    return decorator


@argument_type_validator({"text": str})
def parse_plateau(text: str) -> dict[str, int]:
    """
    Parses the "plateau" line of a mission input to return a dictionary
    containing the maximum x and y coordinates of the mission grid.

    Args:
        text: The plateau data in string format with x and y coordinates
            separated by a space e.g. "4 6". The x coordinate (4) is the
            first value and the y coordinate (6) is the second value

    Returns:
        A dictionary in the format: {"max_x": 4, "max_y": 6}
    """
    valid_format = r"^\d{1,2} \d{1,2}$"
    regex = re.compile(valid_format)
    if regex.fullmatch(text) == None:
        raise InvalidPlateauError(
            f"Plateau data must be two numbers of two digits max with a single space "
            f"between them in the format 'x y'. Got {text}"
        )

    values = text.split(" ")
    values_int = [*map(int, values)]
    return {"max_x": values_int[0], "max_y": values_int[1]}


@argument_type_validator({"text": str})
def parse_position(text: str) -> dict[str, int | CompassDirection]:
    """
    Parses the position line of a rover from the mission data input and
    returns the values in a dictionary

    Args:
        text: A string representing the position of the rover on the mission
        grid. The string must be in the format "x y direction" where x is the
        rover's x coordinate, y is the rover's y coordinate and direction is
        the direction the rover is facing. This must be a single character
        representing one of the four cardinal compass points e.g. N = North,
        E = East, S = South, W = West. The three values must be separated by a
        single space.

    Returns:
        A dictionary in the format: {"x": 1, "y": 2, "direction": "N"}
        Note:- The x and y coordinates are returned as integers.
    """
    valid_format = r"^\d{1,2} \d{1,2} [NESW]$"
    regex = re.compile(valid_format)
    if regex.fullmatch(text) == None:
        raise InvalidPositionError(
            f"Position data must be two numbers of two digits max and a direction "
            f"value of N, E, S or W with a single space between each value e.g. "
            f"'1 2 E'. Got {text}"
        )

    values = text.split(" ")
    return {
        "x": int(values[0]),
        "y": int(values[1]),
        "direction": CompassDirection(values[2]),
    }


@argument_type_validator({"text": str})
def parse_instructions(text: str) -> list[Instruction]:
    """
    Parses a rover's instructions line and returns the instructions as
    a list of Instruction enum class instances.

    Args:
        text: A text string representing the rover's instructions where
        each character in the string represents a distinct instruction.
        Only the characters "L", "M" and "R" should be used where:
            L = Rotate the rover 90deg to the left
            M = Move the rover one square forward in the direction it is facing
            R = Rotate the rover 90deg to the right

    Returns:
        A list containing each instruction as an instance of the Instruction enum class.
        e.g. "LMR" input would return [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]
    """
    # valid_format = r"^[LMR]+$"
    # regex = re.compile(valid_format)
    # if regex.fullmatch(text) == None:
    #     raise InvalidInstructionError(
    #         f"Instructions data must be a single continuous string comprising only "
    #         f"the character 'L' for rotate left, 'R' for rotate right or 'M' for move "
    #         f"forward one space. Got {text}"
    #     )

    try:
        instruction_list = [Instruction(char) for char in text]
        return instruction_list

    except ValueError as err:
        logger.error(f"Function parse_instructions received an invalid argument: {err}")
        raise InvalidInstructionError(err)


@argument_type_validator({"text": str})
def parse_mission(text: str) -> dict[str, dict | list]:
    """
    Parses an entire mission input and returns the data in a formatted
    dictionary.

    Args:
        text: The mission data in string format e.g.
            5 5
            1 2 N
            LMLMLMLMM
            3 3 E
            MMRMMRMRRM

            Where the first line is the dimensions of the plateau and
            subsequent lines represent the position and instructions
            for each rover. Each rover has two lines associated with it:
            the first is the rover's position (1 2 N) and the second is
            that rover's instructions (LMLMLMLMM)

        Returns:
            Dictionary in the format:
            {
                "plateau": {"max_x": 5, "max_y": 5},
                "rovers": [
                    {
                        "position": {"x": 1, "y": 2, "direction": CompassDirection.NORTH},
                        "instructions": ["L", "M", "L", "M", "L", "M", "L", "M", "M"]
                    },
                    {
                        "position": {"x": 3, "y": 3, "direction": CompassDirection.EAST},
                        "instructions": ["M", "M", "R", "M", "M", "R", "M", "R", "R", "M"]
                    }
                ]
            }

    """
    mission_lines = [*enumerate(text.split("\n"))]

    parsed_mission = {"plateau": {}, "rovers": []}
    for line in range(len(mission_lines)):
        # First line of the input string is always the "plateau" line
        if mission_lines[line][0] == 0:
            parsed_mission["plateau"] = parse_plateau(mission_lines[line][1])
        # The odd numbered row indexes will always be the "position" line
        # and even numbered lines will always be the "instructions" line
        elif mission_lines[line][0] % 2 == 1:
            # Exit the loop if an empty mission line is encountered e.g.
            # if the final line with content has a newline character at
            # the end of it causing the loop to iterate on to the next
            # blank line
            if mission_lines[line][1] == "":
                break
            rover = {
                "position": parse_position(mission_lines[line][1]),
                "instructions": parse_instructions(mission_lines[line + 1][1]),
            }
            parsed_mission["rovers"].append(rover)

    return parsed_mission


def load_mission_from_file(path: str | Path) -> str:
    """
    Reads the file located at path and returns its contents as a string.

    Args:
        path: the filepath of the file to be read as either a string or Path object

    Returns:
        The contents of the read file as a string

    Raises:
        TypeError: If argument passed as path is not string or Path object type
        FileNotFoundError: If no file could be found at the path provided as the path argument
    """
    if not isinstance(path, (str, Path)):
        raise TypeError(f"Expected type str or Path as path argument. Got {type(path)}")

    with open(path, "r") as file:
        mission_text = file.read()

    return mission_text
