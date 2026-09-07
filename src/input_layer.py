def parse_plateau(text: str) -> dict[str, int]:
    values = text.split(" ")
    values_int = [*map(int, values)]
    return {"max_x": values_int[0], "max_y": values_int[1]}
