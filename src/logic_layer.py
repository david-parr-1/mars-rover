from src.custom_enums import CompassDirection, Instruction, RoverType
from src.logging_config import get_logger

logger = get_logger(__name__)

ROTATIONS = {
    CompassDirection.NORTH: {
        Instruction.LEFT: CompassDirection.WEST,
        Instruction.RIGHT: CompassDirection.EAST,
    },
    CompassDirection.EAST: {
        Instruction.LEFT: CompassDirection.NORTH,
        Instruction.RIGHT: CompassDirection.SOUTH,
    },
    CompassDirection.SOUTH: {
        Instruction.LEFT: CompassDirection.EAST,
        Instruction.RIGHT: CompassDirection.WEST,
    },
    CompassDirection.WEST: {
        Instruction.LEFT: CompassDirection.SOUTH,
        Instruction.RIGHT: CompassDirection.NORTH,
    },
}

MOVEMENTS = {
    CompassDirection.NORTH: {"x_change": 0, "y_change": 1},
    CompassDirection.EAST: {"x_change": 1, "y_change": 0},
    CompassDirection.SOUTH: {"x_change": 0, "y_change": -1},
    CompassDirection.WEST: {"x_change": -1, "y_change": 0},
}

MOVEMENT_SPEED = {
    RoverType.CARGO: 2,
    RoverType.SCIENCE: 1,
}


def rotate(
    position: dict[str, int | CompassDirection], instruction: Instruction
) -> dict[str, int | CompassDirection]:
    """
    Takes a rover's position dictionary and returns a new dictionary with the direction value
    updated in accordance with the instruction argument passed

    Args:
        `position`: A rover's position dictionary in the format:
        ```
        {
            "x": 1,
            "y": 2,
            "direction": "N"
        }
        ```

        `instruction`: A instruction enum class object representing the direction in which the
        rover is to be turned e.g. Instruction.LEFT or Instruction.RIGHT

    Returns:
        A new dictionary in the same format as the input but with the direction value updated
        to the new value after rotation
    """
    start_direction = position["direction"]
    if not isinstance(start_direction, CompassDirection):
        logger.error(
            f"rotate() function received non CompassDirection enum direction value in position "
            f"argument: {position}"
        )
        raise TypeError(
            f"The `direction` value of the position dictionary must be of enum type "
            f"CompassDirection. Got {type(start_direction)}"
        )

    rotated_direction = ROTATIONS[start_direction][instruction]
    updated_position = {**position, "direction": rotated_direction}
    return updated_position


def move(
    position: dict[str, int | CompassDirection], plateau: dict[str, int]
) -> dict[str, CompassDirection | int]:
    """
    Takes a rover's position dictionary along with a mission plateau dictionary and
    calculates the rover's new position on the map by moving it one place in the direction
    that it is facing as defined by the `direction` key value in the rover's position
    dictionary. NOTE:- if the move would take the rover outside of either the maximum x
    or maximum y values of the passed plateau dictionary, the function will not updated
    the rover's position values and returned unchanged x and y positions.

    Args:
        `position`: A rover's position dictionary in the format:
        ```
        {
            "x": 1,
            "y": 2,
            "direction": CompassDirection()
        }
        ```

        `plateau`: A dictionary containing the maximum x and y value of the mission map.
        Format example: `{"max_x": 5, "max_y": 5}`

    Returns:
        If the rover's move does not move it beyond the maximum x and y values of the mission plateau,
        returns a new dictionary in the same format as the input but with the x or y values updated
        to the new values after rotation. If the rover's move does move it beyond the maximum x or
        y values of the mission plateau, a dictionary is returned with unchanged x and y values.
    """
    if not isinstance(position["x"], int):
        logger.error(
            f"move() function received invalid x value in position argument: {position}"
        )
        raise TypeError(
            f"The `x` value of the position dictionary must be an integer. Got {type(position['x'])}"
        )

    if not isinstance(position["y"], int):
        logger.error(
            f"move() function received invalid y value in position argument: {position}"
        )
        raise TypeError(
            f"The `y` value of the position dictionary must be an integer. Got {type(position['x'])}"
        )

    if not isinstance(position["direction"], CompassDirection):
        logger.error(
            f"move() function received invalid direction value in position argument: {position}"
        )
        raise TypeError(
            f"The `direction` value of the position dictionary must be a string. Got {type(position['direction'])}"
        )

    updated_position = {**position}
    updated_x = position["x"] + MOVEMENTS[position["direction"]]["x_change"]
    updated_y = position["y"] + MOVEMENTS[position["direction"]]["y_change"]

    # If the updated positions take the rover outside of the plateau then the position
    # dictionary should be returned unchanged
    if not 0 <= updated_x <= plateau["max_x"] or not 0 <= updated_y <= plateau["max_y"]:
        logger.warning(
            f"Rover has reached edge of mission plateau. Move {position['direction']} "
            f"has been ignored from position x: {position['x']} y: {position['y']}"
        )
        return updated_position

    updated_position["x"] = updated_x
    updated_position["y"] = updated_y

    return updated_position


def execute_instructions(
    position: dict[str, CompassDirection | int],
    instructions: list[Instruction],
    plateau: dict[str, int],
) -> dict[str, CompassDirection | int]:
    """
    Takes a rover's starting position, a list of instructions and a plateau dictionary and processes
    the instructions to return an updated position dictionary.

    Args:
        `position`: A rover's position dictionary in the format:
        ```
        {
            "x": 1,
            "y": 2,
            "direction": CompassDirection()
        }
        ```

        `instructions`: A list of Instruction enum class instances representing the instructions that
        the rover is to follow to reach its final position. `Instruction.LEFT` and `Instruction.RIGHT` rotate
        the rover left or right respectively. `Instruction.MOVE` moves the rover forward one space in the
        direction defined by the value of the `direction` key within its `position` dictionary.

        `plateau`: A dictionary containing the maximum x and y value of the mission map.
        Format example: `{"max_x": 5, "max_y": 5}`

    Returns:
        A dictionary representing the rover's final position once all instructions have been
        processed.
    """
    logger.info(f"Starting execution of instructions for rover at position: {position}")
    updated_position = {**position}

    for instruction in instructions:
        if instruction == Instruction.MOVE:
            updated_position = move(updated_position, plateau)
        else:
            updated_position = rotate(updated_position, instruction)

    logger.info(
        f"Completed execution of instructions. Start position was: {position} | "
        f"Final position is: {updated_position}"
    )

    return updated_position
