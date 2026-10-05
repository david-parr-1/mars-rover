from datetime import datetime, timezone
from pathlib import Path

from src.classes import Mission, Plateau, Position, Rover
from src.exceptions import (
    InvalidInstructionError,
    InvalidPlateauError,
    InvalidPositionError,
)
from src.input_layer import parse_mission
from src.logging_config import get_logger

logger = get_logger(__name__)


def execute_mission(
    mission_text: str, archive_path: Path | str = Path("mission_archive")
) -> str | None:
    """
    Takes a mission in string format and executes the instructions for each rover the mission contains. If the input string is valid, a string containing each rover's new position after execution of its instruction is returned. If input is invalid, the function aborts and prints the reason to the terminal.

    :param mission_text: The size of the mission plateau followed by each rover's position
        and the movement instructions it is required to execute.
        The format of the string must be:\n
        "5 5"  # Plateau size x y\n
        "1 2 N"  # Position of the first rover x y direction\n
        "LMR"  # Instructions for the first rover to execute\n
        "3 3 E"  # Position of the nth rover\n
        "RML"  # Instructions for the nth rover to execute\n
    :type mission_text: str
    :param archive_path: The path to save the mission archive in JSON format.
    :type archive_path: str or Path

    :rtype: str
    :returns: A string containing the final positions of each rover on a new line:

        0 2 N S\n
        3 2 E C\n
    """
    try:
        mission = Mission()
        mission.timestamp = datetime.now(timezone.utc)
        logger.info(f"Starting mission execution at {mission.timestamp}")
        parsed_mission = parse_mission(mission_text)
        plateau_max_dims = parsed_mission["plateau"]
        mission.plateau = Plateau(plateau_max_dims["max_x"], plateau_max_dims["max_y"])

        rovers = parsed_mission["rovers"]
        for each in rovers:
            rover_start_position = Position(
                each["position"]["x"],
                each["position"]["y"],
                each["position"]["direction"],
            )
            rover_instructions = each["instructions"]
            rover_type = each["position"]["rover_type"]
            rover = Rover(
                rover_start_position, rover_instructions, mission.plateau, rover_type
            )
            mission.add_rover(rover)

        consolidated_output = []
        for rover in mission.rovers:
            rover.execute_instructions(mission.plateau)

            # This function is require to return the final position of each
            # rover as a string in the below format:
            # 1 3 N S
            # 5 1 E C
            str_output = " ".join(
                [
                    str(rover.latest_position.x),
                    str(rover.latest_position.y),
                    str(rover.latest_position.direction.value),
                    str(rover.rover_type.value),
                ]
            )
            consolidated_output.append(str_output)

        # Missions are required to be archived
        mission.archive(archive_path)

        return "\n".join(consolidated_output)

    except (InvalidPlateauError, InvalidPositionError, InvalidInstructionError) as err:
        logger.error(f"Mission execution aborted: {err}")
        print(f"Mission execution aborted: {err}")
