import pytest

from src.input_layer import parse_instructions, parse_plateau, parse_position


def test_parse_plateau_returns_dictionary():
    result = parse_plateau("5 5")

    assert isinstance(result, dict)


def test_parse_plateau_returns_correct_schema():
    result = parse_plateau("5 5")

    assert all(isinstance(k, str) and isinstance(v, int) for k, v in result.items())


def test_parse_plateau_returns_correct_x_y_values():
    mock_string_1 = "5 5"
    mock_string_2 = "4 6"

    result_1 = parse_plateau(mock_string_1)
    result_2 = parse_plateau(mock_string_2)

    assert result_1 == {"max_x": 5, "max_y": 5}
    assert result_2 == {"max_x": 4, "max_y": 6}


def test_parse_position_returns_dictionary():
    result = parse_position("1 2 N")

    assert isinstance(result, dict)


def test_parse_position_returns_correct_schema():
    result = parse_position("1 2 N")

    assert all(
        isinstance(k, str) and isinstance(v, (int, str)) for k, v in result.items()
    )


@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [1, 2])
@pytest.mark.parametrize("direction", ["N", "E", "S", "W"])
def test_parse_position_returns_correct_position_values(x: int, y: int, direction: str):
    inputs = [str(x), str(y), direction]
    mock_string = " ".join(inputs)

    result = parse_position(mock_string)

    assert result == {"x": x, "y": y, "direction": direction}


def test_parse_instructions_returns_list():
    mock_instructions = "LMLMLMLMM"

    result = parse_instructions(mock_instructions)

    assert isinstance(result, list)


def test_parse_instructions_returns_single_instruction_list():
    mock_instructions = "L"

    result = parse_instructions(mock_instructions)

    assert result == ["L"]


@pytest.mark.parametrize(
    "mock_instruction,expected_result",
    [
        ("LMR", ["L", "M", "R"]),
        ("RMML", ["R", "M", "M", "L"]),
        ("MRMLM", ["M", "R", "M", "L", "M"]),
    ],
)
def test_parse_instructions_returns_multi_instruction_list_in_right_order(
    mock_instruction, expected_result
):
    result = parse_instructions(mock_instruction)

    assert result == expected_result
