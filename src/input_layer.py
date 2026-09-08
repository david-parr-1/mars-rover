from pathlib import Path


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
    values = text.split(" ")
    values_int = [*map(int, values)]
    return {"max_x": values_int[0], "max_y": values_int[1]}


def parse_position(text: str) -> dict[str, int | str]:
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
    values = text.split(" ")
    return {"x": int(values[0]), "y": int(values[1]), "direction": values[2]}


def parse_instructions(text: str) -> list[str]:
    """
    Parses a rover's instructions line and returns the instructions as
    a list.

    Args:
        text: A text string representing the rover's instructions where
        each character in the string represents a distinct instruction.
        Only the characters "L", "M" and "R" should be used where:
            L = Rotate the rover 90deg to the left
            M = Move the rover one square forward in the direction it is facing
            R = Rotate the rover 90deg to the right

    Returns:
        A list containing each instruction as a distinct element
        e.g. "LMR" input would return ["L", "M", "R"]
    """
    return [char for char in text]


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
                        "position": {"x": 1, "y": 2, "direction": "N"},
                        "instructions": ["L", "M", "L", "M", "L", "M", "L", "M", "M"]
                    },
                    {
                        "position": {"x": 3, "y": 3, "direction": "E"},
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


if __name__ == "__main__":
    mission = load_mission_from_file(Path("data/sample.mission"))
    mission_data = parse_mission(mission)
    print(mission_data)
