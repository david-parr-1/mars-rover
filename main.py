import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path

from src.classes import Mission, Plateau, Position, Rover
from src.exceptions import (
    InvalidInstructionError,
    InvalidPlateauError,
    InvalidPositionError,
)
from src.input_layer import (
    parse_mission,
    validate_instructions_from_input,
    validate_rover_type_from_input,
)
from src.logging_config import get_logger
from src.text_colours import BLUE_BOLD, BOLD, GREEN_BOLD, ORANGE_BOLD, RESET

logger = get_logger(__name__)


def execute_mission(
    mission_to_execute: str | Mission,
    archive_path: Path | str = Path("mission_archive"),
) -> str | None:
    """
    Execute each rover's instructions in the passed mission.

    If the input is valid, a string containing each rover's new position
    after execution of its instruction is returned. The output is saved to
    disk as a JSON file at the path passed to `archive_path`. If input is
    invalid, the function aborts and prints the reason to the terminal.

    Args:
        mission: Can be an instance of `Mission` or a string. If a string,
            the format of the string must be:
                "5 5"  # Plateau size x y
                "1 2 N"  # Position of the first rover x y direction
                "LMR"  # Instructions for the first rover to execute
                "3 3 E"  # Position of the nth rover
                "RML"  # Instructions for the nth rover to execute
        archive_path: The path to save the mission archive in JSON format.

    Returns: A string containing the final positions of each rover on a new line:

        '0 2 N S'
        '3 2 E C'
    """
    if not os.path.exists(archive_path):
        err_msg = (
            f"The specified path {archive_path} could not be "
            f"found. Please choose a valid filepath and retry "
            f"execution."
        )
        logger.error(err_msg)
        print(err_msg)
        return

    if isinstance(mission_to_execute, Mission):
        mission = deepcopy(mission_to_execute)
    else:
        try:
            mission = Mission()
            mission.timestamp = datetime.now(timezone.utc)
            logger.info(f"Starting mission execution at {mission.timestamp}")
            parsed_mission = parse_mission(mission_to_execute)
            plateau_max_dims = parsed_mission["plateau"]
            mission.plateau = Plateau(
                plateau_max_dims["max_x"], plateau_max_dims["max_y"]
            )

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
                    rover_start_position,
                    rover_instructions,
                    mission.plateau,
                    rover_type,
                )
                mission.add_rover(rover)

        except (
            InvalidPlateauError,
            InvalidPositionError,
            InvalidInstructionError,
        ) as err:
            logger.error(f"Mission execution aborted: {err}")
            print(f"Mission execution aborted: {err}")

    # Execute mission
    mission_str = mission.execute(archive_path)
    return mission_str


def mission_cli() -> str | None:
    """
    Construct a `Mission` from user prompting.

    The function gives the user successive terminal prompts to input the
    required mission plateau and rover details. Invalid responses are
    reported to the user and the prompt is given again to retry entry.
    Once all mission details have been input and the user chooses not to
    add another rover, the mission is executed and written to disk as a
    JSON file. The file is written to path `./mission_archive`.
    """
    mission = Mission()
    plateau = Plateau.from_input()

    # Plateau.from_input() returns None if the user entered 'abort'
    # so mission processing should stop.
    if plateau is None:
        print(f"{BOLD}Mission loading aborted.{RESET}")
        return None

    mission.plateau = plateau

    # Add rovers

    rovers_completed = False
    while not rovers_completed:
        rover_count = len(mission.rovers)
        print(
            f"\nThere are {rover_count} rovers so far. Enter details of "
            f"rover number {rover_count + 1}...\n"
        )
        rover_type = validate_rover_type_from_input()
        if rover_type is None:
            print(f"{BOLD}Mission loading aborted.{RESET}")
            return None

        start_position = Position.from_input(plateau=mission.plateau)
        if start_position is None:
            print(f"{BOLD}Mission loading aborted.{RESET}")
            return None

        instructions = validate_instructions_from_input()
        if instructions is None:
            print(f"{BOLD}Mission loading aborted.{RESET}")
            return None

        rover = Rover(
            start_position, instructions, mission.plateau, rover_type=rover_type
        )
        mission.add_rover(rover)

        another_rover = input(
            f"\n{GREEN_BOLD}Rover added to mission successfully.{RESET}\n\n"
            f"Enter {ORANGE_BOLD}'yes'{RESET} to add another "
            f"rover to the mission or enter {ORANGE_BOLD}'no'{RESET} to execute "
            f"the mission.\n\n"
            f"{BLUE_BOLD}Enter 'yes' or 'no': {RESET}"
        )
        if another_rover.lower() == "no":
            rovers_completed = True

    mission.timestamp = datetime.now(timezone.utc)

    mission_str = mission.execute()

    return mission_str


if __name__ == "__main__":
    mission_cli()
