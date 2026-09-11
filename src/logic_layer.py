ROTATIONS = {
    "N": {"L": "W", "R": "E"},
    "E": {"L": "N", "R": "S"},
    "S": {"L": "E", "R": "W"},
    "W": {"L": "S", "R": "N"},
}

MOVEMENTS = {
    "N": {"x_change": 0, "y_change": 1},
    "E": {"x_change": 1, "y_change": 0},
    "S": {"x_change": 0, "y_change": -1},
    "W": {"x_change": -1, "y_change": 0},
}


def rotate(position: dict[str, int | str], instruction: str) -> dict[str, int | str]:
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

        `instruction`: A string representing the direction in which the rover is to be turned
        of the value "L" or "R" representing left and right respectively

    Returns:
        A new dictionary in the same format as the input but with the direction value updated
        to the new value after rotation
    """
    start_direction = position["direction"]
    if not isinstance(start_direction, str):
        raise TypeError(
            f"The `direction` value of the position dictionary must be a string. Got {type(start_direction)}"
        )

    rotated_direction = ROTATIONS[start_direction][instruction]
    updated_position = {**position, "direction": rotated_direction}
    return updated_position


def move(
    position: dict[str, str | int], plateau: dict[str, int]
) -> dict[str, str | int]:
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
            "direction": "N"
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
        raise TypeError(
            f"The `x` value of the position dictionary must be an integer. Got {type(position['x'])}"
        )

    if not isinstance(position["y"], int):
        raise TypeError(
            f"The `y` value of the position dictionary must be an integer. Got {type(position['x'])}"
        )

    if not isinstance(position["direction"], str):
        raise TypeError(
            f"The `direction` value of the position dictionary must be a string. Got {type(position['direction'])}"
        )

    updated_position = {**position}
    updated_x = position["x"] + MOVEMENTS[position["direction"]]["x_change"]
    updated_y = position["y"] + MOVEMENTS[position["direction"]]["y_change"]

    # If the updated positions take the rover outside of the plateau then the position
    # dictionary should be returned unchanged
    if not 0 <= updated_x <= plateau["max_x"] or not 0 <= updated_y <= plateau["max_y"]:
        return updated_position

    updated_position["x"] = updated_x
    updated_position["y"] = updated_y

    return updated_position
