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
    Take a rover's position dictionary and rotate its direction by 90degs.

    Args:
        position: A dictionary of a rover's position.
        instruction: The direction in which the rover will rotate.

    Returns:
        A new dictionary in the same format as the input but with the direction
        value updated to the new value after rotation

    Examples:
        >>> rover_position = {'x': 1, 'y': 2, 'direction': CompassDirection.NORTH}
        >>> rotate(rover_position, Instruction.RIGHT)
        {'x': 1, 'y': 2, 'direction': CompassDirection.EAST}
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
    Take a rover's position dictionary and move it once in the direction it is facing.

    If the move would take the rover outside of either the maximum x or maximum y
    values of the passed plateau dictionary, the function will not updated the
    rover's position values and returned unchanged x and y positions.

    Args:
        position: A dictionary of a rover's position.
        plateau: A dictionary of the mission plateau's `max_x` and `max_y` values.

    Returns:
        A new dictionary of the rover's updated position in the same format as the
            input dictionary. If the rover's move would have taken the rover beyond
            the bounds of the mission plateau, a new dictionary is returned with
            the rover's position unchanged.

    Examples:
        **Move the rover once to the North.**
        >>> rover_position = {'x': 1, 'y': 2, 'direction': CompassDirection.NORTH}
        >>> plateau = {'max_x': 5, 'max_y': 5}
        >>> move(rover_position, plateau)
        {'x': 1, 'y': 3, 'direction': CompassDirection.NORTH}

        **Move the rover once to the East**
        >>> rover_position = {'x': 1, 'y': 2, 'direction': CompassDirection.EAST}
        >>> plateau = {'max_x': 5, 'max_y': 5}
        >>> move(rover_position, plateau)
        {'x': 2, 'y': 2, 'direction': CompassDirection.EAST}

        **Attempt to move the rover beyond the plateau bounds**
        >>> rover_position = {'x': 5, 'y': 5, 'direction': CompassDirection.EAST}
        >>> plateau = {'max_x': 5, 'max_y': 5}
        >>> move(rover_position, plateau)
        {'x': 5, 'y': 5, 'direction': CompassDirection.EAST}
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
    Execute a list of instructions in turn for a rover and return a new position.

    The position is returned as a new dictionary.

    Args:
        position: A dictionary of a rover's position.
        instructions: A list of members of the Instruction enum. Each element of
            list is a navigational instruction to be carried out by the rover.
        plateau: A dictionary containing the maximum x and y value of the mission
            map. Format example: `{"max_x": 5, "max_y": 5}`

    Returns:
        A dictionary representing the rover's final position once all instructions have been
        processed.

    Examples:
        >>> rover_position = {'x': 1, 'y': 2, 'direction': CompassDirection.NORTH}
        >>> instructions = [Instruction.MOVE, Instruction.RIGHT, Instruction.MOVE]
        >>> plateau = {'max_x': 5, 'max_y': 5}
        >>> execute_instructions(rover_position, instructions, plateau)
        {'x': 2, 'y': 3, 'direction': CompassDirection.EAST}
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
