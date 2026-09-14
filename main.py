from typing import cast

from src.input_layer import parse_mission
from src.logic_layer import execute_instructions


def execute_mission(mission: str) -> str:
    """
    Takes a mission in string format and executes the instructions for each rover the
    mission contains. Returns a string containing each rover's new position after
    execution of its instructions

    Args:
        `mission`: A string containing the size of the mission plateau along with each
        rover's position and movement instructions it is required to execute. The
        format of the string must be:
        ```python
        "5 5"  # Plateau size x y
        "1 2 N"  # Position of the first rover x y direction
        "LMR"  # Instructions for the first rover to execute
        "3 3 E"  # Position of the nth rover
        "RML"  # Instructions for the nth rover to execute
        ```

    Returns:
        A string containing the final positions of each rover on a new line:
        ```
        0 2 N
        3 2 E
        ```
    """
    parsed_mission = parse_mission(mission)
    plateau = cast(dict[str, int], parsed_mission["plateau"])
    rover_final_positions = []
    for rover in parsed_mission["rovers"]:
        rover_position = rover["position"]
        rover_instructions = rover["instructions"]
        rover_new_position = execute_instructions(
            rover_position, rover_instructions, plateau
        )
        rover_new_position_str = " ".join(
            [str(value) for value in rover_new_position.values()]
        )
        rover_final_positions.append(rover_new_position_str)

    return "\n".join(rover_final_positions)
