def parse_plateau(text: str) -> dict[str, int]:
    values = text.split(" ")
    values_int = [*map(int, values)]
    return {"max_x": values_int[0], "max_y": values_int[1]}


def parse_position(text: str) -> dict[str, int | str]:
    values = text.split(" ")
    return {"x": int(values[0]), "y": int(values[1]), "direction": values[2]}


def parse_instructions(text: str) -> list[str]:
    return [char for char in text]
