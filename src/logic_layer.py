ROTATIONS = {
    "N": {"L": "W", "R": "E"},
    "E": {"L": "N", "R": "S"},
    "S": {"L": "E", "R": "W"},
    "W": {"L": "S", "R": "N"},
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
