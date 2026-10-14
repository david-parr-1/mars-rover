import inspect
import re
from collections.abc import Callable
from functools import wraps
from pathlib import Path
from typing import Any

from src.custom_enums import CompassDirection, Instruction, RoverType
from src.exceptions import (
    InvalidInstructionError,
    InvalidPlateauError,
    InvalidPositionError,
)
from src.logging_config import get_logger
from src.text_colours import BLUE_BOLD, ORANGE_BOLD, RED_BOLD, RESET

logger = get_logger(__name__)


def argument_type_validator(
    argument_types: dict[str, type | tuple[type, ...]],
) -> Callable[..., Callable[..., Any]]:
    """Create a decorator that validates a function's argument types.

    Args:
        argument_types: Mapping from parameter names to accepted types.
            Use a tuple to allow multiple types for a parameter.

    Returns:
        A decorator that checks argument types before calling the function.

    Raises:
        TypeError: When a decorated function is called with an argument
            whose type is not among the types specified for that parameter.
    """

    def decorator(func) -> Callable[..., Any]:
        sig = inspect.signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_args = sig.bind(*args, **kwargs)
            for arg in bound_args.arguments:
                # Instance and class arguments are supplied by Python, not callers.
                if arg in {"self", "cls"}:
                    continue
                arg_value = bound_args.arguments[arg]

                # The specified valid data type(s) are stored in a tuple if they are not in
                # one already to simplify the type validation.
                expected_types = argument_types[arg]
                if not isinstance(expected_types, tuple):
                    valid_types = (expected_types,)
                else:
                    valid_types = expected_types

                type_is_valid = [
                    isinstance(arg_value, element) for element in valid_types
                ]

                if not any(type_is_valid):
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
    """Parses the "plateau" line of a mission input to return a dictionary.

    The returned dictionary contains the maximum x and y coordinates of
    the mission grid.

    The supplied x and y values must both be greater than 0.

    Args:
        text: The plateau data in string format with x and y coordinates
            separated by a space e.g. `'4 6'`. The x coordinate (`4`) is the
            first value and the y coordinate (`6`) is the second value

    Returns:
        A dictionary containing the `max_x` and `max_y` properties of the
            plateau

    Raises:
        InvalidPlateauError: if argument passed is in an invalid format or
            `x` or `y` values are not both greater than `0`.

    Examples:
        >>> parse_plateau('4 6')
        {'max_x': 4, 'max_y': 6}
    """
    valid_format = r"^\d{1,2} \d{1,2}$"
    regex = re.compile(valid_format)
    if regex.fullmatch(text) == None:
        raise InvalidPlateauError(
            f"\n{RED_BOLD}ERROR:{RESET} Plateau data must be two numbers of two digits max with a "
            f"single space between them in the format 'x y'. Got {text}\n"
        )

    values = text.split(" ")
    values_int = [*map(int, values)]
    max_x, max_y = values_int

    # Plateau max_x and max_y values must be greater than zero or the Plateau
    # will only be one dimensional.
    if max_x <= 0 or max_y <= 0:
        raise InvalidPlateauError(
            f"Plateau max_x and max_y values must be greater than 0. Got "
            f"x: {max_x} | y: {max_y}"
        )

    return {"max_x": max_x, "max_y": max_y}


@argument_type_validator({"text": str})
def parse_position(text: str) -> dict[str, int | CompassDirection | RoverType]:
    """
    Parses a rover's position line from the mission input and returns as a dict.

    The line contains the rover's `x` and `y` coordinates and facing
    direction. It may also include a rover type. Values must be separated
    by single spaces.

    Args:
        text: Position in the format ``x y direction [rover_type]``.
            The direction must be ``N``, ``E``, ``S``, or ``W``. The optional
            rover type must be ``C`` (Cargo) or ``S`` (Science).

    Returns:
        A dictionary containing integer coordinates, the direction, and the rover type.

    Raises:
        InvalidPositionError: When the argument passed to ``text`` does not
            conform to the format requirementss

    Example:

    .. code-block:: python

        {"x": 1, "y": 2, "direction": CompassDirection.NORTH, "rover_type": RoverType.CARGO}
    """
    text_cleaned = re.sub("[ +]", " ", text)

    valid_format = r"^\d{1,2} \d{1,2} [NESW](?: [CS])?$"
    regex = re.compile(valid_format)
    if regex.fullmatch(text_cleaned) == None:
        raise InvalidPositionError(
            f"\n{RED_BOLD}ERROR:{RESET} Position data must be either:\n"
            f"  - Two numbers of two digits max and a direction value of N, E, "
            f"S or W with a single space between each value e.g. '1 2 E' or;\n"
            f"  - Two numbers of two digits max, a direction value of N, E, "
            f"S or W and either the S or C character to denote the rover type "
            f"where C = Cargo Rover and S = Science Rover. There must be a "
            f"single space between each character e.g. '1 2 E S'\n"
            f"Got {text}"
        )

    values = text.split(" ")
    rover_type = RoverType(values[3]) if len(values) == 4 else RoverType.SCIENCE

    parsed_position = {
        "x": int(values[0]),
        "y": int(values[1]),
        "direction": CompassDirection(values[2]),
        "rover_type": rover_type,
    }

    return parsed_position


@argument_type_validator({"text": str})
def parse_instructions(text: str) -> list[Instruction]:
    """Parse a rover's instruction string into instruction enum members.

    Each character represents one instruction. Only `L`, `M`, and `R` are
    accepted; the input must not contain spaces or other separators.

    Args:
        text: A sequence of rover instruction characters.

    Returns:
        The corresponding `Instruction` enum members, in input order.
        An empty string returns an empty list.

    Raises:
        InvalidInstructionError: If `text` contains an unsupported character.

    Examples:
        >>> parse_instructions("LMR")
        [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]
    """
    try:
        instruction_list = [Instruction(char) for char in text]
        return instruction_list

    except ValueError as err:
        logger.error(f"Function parse_instructions received an invalid argument: {err}")
        raise InvalidInstructionError(err)


@argument_type_validator({"text": str})
def parse_mission(text: str) -> dict[str, dict | list]:
    """Parse a mission input and return the data in a formatted dictionary.

    Args:
        text: The mission data in string format e.g.\n
            5 5\n
            1 2 N\n
            LMLMLMLMM\n
            3 3 E\n
            MMRMMRMRRM\n
            Where the first line is the dimensions of the plateau and
            subsequent lines represent the position and instructions
            for each rover. Each rover has two lines associated with it -\n
                The first is the rover's position (`1 2 N`)\n
                The second is that rover's instructions (`LMLMLMLMM`).

    Returns:
        A dictionary containing the parsed mission's data.

    Examples:
        >>> mission = (
        ...     "5 5\\n"
        ...     "1 2 N\\n"
        ...     "LMLMLMLMM\\n"
        ...     "3 3 E\\n"
        ...     "MMRMMRMRRM"
        )
        >>> result = parse_mission(mission)
        >>> result["plateau"]
        {'max_x': 5, 'max_y': 5}
        >>> print(len(result.rovers()))
        2
    """
    mission_lines = [*enumerate(text.split("\n"))]
    total_mission_lines = len(mission_lines)

    parsed_mission = {"plateau": {}, "rovers": []}
    for line in range(total_mission_lines):
        line_number = mission_lines[line][0]
        line_text = mission_lines[line][1]
        # First line of the input string is always the "plateau" line
        if line_number == 0:
            parsed_mission["plateau"] = parse_plateau(line_text)
        # Thereafter, each odd numbered row index will always be a single rover's
        # "position" line. The even numbered line that follows the odd-numbered line
        # will always be that rover's "instructions" line
        elif line_number % 2 == 1:
            # Exit the loop if an empty mission line is encountered e.g.
            # if the final line with content has a newline character at
            # the end of it causing the loop to iterate on to the next
            # blank line
            if line_text == "":
                break

            next_line_text = mission_lines[line + 1][1]
            rover = {
                "position": parse_position(line_text),
                "instructions": parse_instructions(next_line_text),
            }
            parsed_mission["rovers"].append(rover)

    return parsed_mission


def load_mission_from_file(path: str | Path) -> str:
    """Read the file located at path and return its contents as a string.

    Args:
        path: the filepath of the file to be read.

    Returns:
        The contents of the file located at `path`.

    Raises:
        TypeError: If argument passed to `path` is not a valid type.
        FileNotFoundError: If no file could be found at `path`.
    """
    if not isinstance(path, (str, Path)):
        raise TypeError(f"Expected type str or Path as path argument. Got {type(path)}")

    with open(path, "r") as file:
        mission_text = file.read()

    return mission_text


def validate_rover_type_from_input() -> RoverType | None:
    """Prompt for user selection of rover type and return as `RoverType` member if valid.

    If the user enters an invalid response an error message is printed and the user
    is prompted again for input.

    `'abort'` can be entered as a user response which will cause this function to
    return `None` which allows the `mission_cli` to abort mission loading.

    Returns:
        A member of the `RoverType` class if user response is valid.
            `None` if user response is `'abort'`.

    Examples:
        When user selects a cargo rover:
            ```
            Prompt: Enter rover type here
            User enters: C
            Return Value: `RoverType.CARGO`
            ```

            When user aborts:
            ```
            Prompt: Enter rover type here
            User enters: abort
            Return Value: None
            ```

    """
    valid_rover_type = False
    while not valid_rover_type:
        user_input = input(
            f"Select the type of rover to add to the mission. Enter "
            f"{ORANGE_BOLD}'S'{RESET} for a science rover or "
            f"{ORANGE_BOLD}'C'{RESET} for a cargo rover.\n\n"
            f"{BLUE_BOLD}Enter rover type here: {RESET}"
        )
        # Return None if the user enters 'abort' so that the mission
        # execution can be cancelled on return of None.
        if user_input == "abort":
            print("Aborting mission loading...")
            return None
        try:
            rover_type = RoverType(user_input)
            valid_rover_type = True
            return rover_type
        except ValueError as err:
            logger.error(err)
            print("".join(["\n", f"{RED_BOLD}ERROR: {RESET}", str(err)]))
            print(
                f"The rover type value must be {ORANGE_BOLD}'S'{RESET} or "
                f"{ORANGE_BOLD}'C'{RESET}. Got {user_input}\n"
                f"Please try entering the rover type again or entering 'abort' "
                f"to abort mission loading."
            )


def validate_instructions_from_input() -> list[Instruction] | None:
    """Prompt for user input of instructions and return as `list` of `Instruction`.

    If the user enters an invalid response an error message is printed and the user
    is prompted again for input.

    `'abort'` can be entered as a user response which will cause this function to
    return `None` which allows the `mission_cli` to abort mission loading.

    Returns:
        A `list` of enum member `Instruction` if user response is valid.
            `None` if user response is `'abort'`.

    Examples:
        When user selects a cargo rover:
            ```
            Prompt: Enter instructions here
            User enters: LMR
            Return Value: `[Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]`
            ```

            When user aborts:
            ```
            Prompt: Enter instructions here
            User enters: abort
            Return Value: None
            ```
    """
    valid_instructions = False
    while not valid_instructions:
        user_input = input(
            f"Enter the instructions that the rover is to follow as a string "
            f"of characters with no spaces e.g. {ORANGE_BOLD}'MMLMMR'{RESET}.\n"
            f"Use {ORANGE_BOLD}'L'{RESET} to rotate the rover left by 90 deg.\n"
            f"Use {ORANGE_BOLD}'R'{RESET} to rotate the rover right by 90 deg.\n"
            f"Use {ORANGE_BOLD}'M'{RESET} to move the rover forward by the number of positions "
            f"according to the rover's type ie. 1 position for a science rover, "
            f"2 positions for a cargo rover.\n\n"
            f"{BLUE_BOLD}Enter instructions here: {RESET}"
        )
        # Return None if the user enters 'abort' so that the mission
        # execution can be cancelled on return of None.
        if user_input == "abort":
            print("Aborting mission loading...")
            return None
        try:
            instructions = parse_instructions(user_input)
            valid_instructions = True
            return instructions
        except InvalidInstructionError as err:
            logger.error(err)
            print("".join(["\n", f"{RED_BOLD}ERROR: {RESET}", str(err)]))
            print(
                f"Instructions must be a string with no spaces "
                f"and contain only the characters L, M, or R. Got "
                f"{user_input}\n"
                f"Please try entering the instructions again or "
                f"entering 'abort' to abort mission loading."
            )
