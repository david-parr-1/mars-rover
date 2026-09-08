def parse_plateau(text: str) -> dict[str, int]:
    values = text.split(" ")
    values_int = [*map(int, values)]
    return {"max_x": values_int[0], "max_y": values_int[1]}


def parse_position(text: str) -> dict[str, int | str]:
    values = text.split(" ")
    return {"x": int(values[0]), "y": int(values[1]), "direction": values[2]}


def parse_instructions(text: str) -> list[str]:
    return [char for char in text]


def parse_mission(text: str) -> dict[str, dict | list]:
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
