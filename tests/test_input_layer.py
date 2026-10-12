import re
from unittest.mock import mock_open, patch

import pytest

from src.custom_enums import CompassDirection, Instruction, RoverType
from src.exceptions import (
    InvalidInstructionError,
    InvalidPlateauError,
    InvalidPositionError,
)
from src.input_layer import (
    argument_type_validator,
    load_mission_from_file,
    parse_instructions,
    parse_mission,
    parse_plateau,
    parse_position,
    validate_instructions_from_input,
    validate_rover_type_from_input,
)


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


@pytest.mark.parametrize(
    "input", [" 5", "5  ", "5  5", "55", "123 1", "1 234", "123 546"]
)
def test_parse_plateau_raises_invalidplateauerror_for_malformed_input(input):
    with pytest.raises(
        InvalidPlateauError,
        match=(
            "Plateau data must be two numbers of two digits max with a single space "
            "between them in the format 'x y'."
        ),
    ):
        parse_plateau(input)


@pytest.mark.parametrize("input_str", ["0 1", "1 0", "0 0"])
def test_parse_plateau_raises_invalidplateauerror_for_values_of_0(input_str):
    with pytest.raises(
        InvalidPlateauError,
        match=(r"^Plateau max_x and max_y values must be greater than 0."),
    ):
        parse_plateau(input_str)


def test_parse_position_returns_dictionary():
    result = parse_position("1 2 N")

    assert isinstance(result, dict)


def test_parse_position_returns_correct_schema():
    result = parse_position("1 2 N")

    assert all(
        isinstance(k, str) and isinstance(v, (int, CompassDirection, RoverType))
        for k, v in result.items()
    )


@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", [1, 2])
@pytest.mark.parametrize("direction", ["N", "E", "S", "W"])
def test_parse_position_returns_correct_position_values(x: int, y: int, direction: str):
    inputs = [str(x), str(y), direction]
    mock_string = " ".join(inputs)

    result = parse_position(mock_string)

    assert result == {
        "x": x,
        "y": y,
        "direction": CompassDirection(direction),
        "rover_type": RoverType.SCIENCE,
    }


@pytest.mark.parametrize(
    "input,expected_rover",
    [
        ("1 2 E S", RoverType.SCIENCE),
        ("1 2 E C", RoverType.CARGO),
    ],
)
def test_parse_position_returns_correct_rover_type_when_rover_type_is_specified(
    input, expected_rover
):
    expected_result = {
        "x": 1,
        "y": 2,
        "direction": CompassDirection.EAST,
        "rover_type": expected_rover,
    }

    result = parse_position(input)

    assert result == expected_result


def test_parse_position_returns_science_rover_type_when_rover_type_is_not_specified():
    expected_result = {
        "x": 1,
        "y": 2,
        "direction": CompassDirection.EAST,
        "rover_type": RoverType.SCIENCE,
    }

    result = parse_position("1 2 E")

    assert result == expected_result


@pytest.mark.parametrize(
    "input",
    [
        "12E",
        "1 2E  ",
        "12 E",
        "1  2 E",
        "111 2 E",
        "1 234 E",
        "123 546",
        "1E",
        "1 2 F",
        "1 2 E T",
        "1 2 ET",
        "1 2 E S ",
    ],
)
def test_parse_position_raises_invalidpositionerror_for_malformed_input(input):
    with pytest.raises(
        InvalidPositionError,
        match=("Position data must be either:"),
    ):
        parse_position(input)


def test_parse_instructions_returns_list():
    mock_instructions = "LMLMLMLMM"

    result = parse_instructions(mock_instructions)

    assert isinstance(result, list)


def test_parse_instructions_returns_single_instruction_list():
    mock_instructions = "L"

    result = parse_instructions(mock_instructions)

    assert result == [Instruction("L")]


@pytest.mark.parametrize(
    "mock_instruction,expected_result",
    [
        ("LMR", [Instruction("L"), Instruction("M"), Instruction("R")]),
        (
            "RMML",
            [Instruction("R"), Instruction("M"), Instruction("M"), Instruction("L")],
        ),
        (
            "MRMLM",
            [
                Instruction("M"),
                Instruction("R"),
                Instruction("M"),
                Instruction("L"),
                Instruction("M"),
            ],
        ),
    ],
)
def test_parse_instructions_returns_multi_instruction_list_in_right_order(
    mock_instruction, expected_result
):
    result = parse_instructions(mock_instruction)

    assert result == expected_result


@pytest.mark.parametrize(
    "input,invalid_character",
    [
        (" LMR", " "),
        ("L MR  ", " "),
        ("LMR ", " "),
        ("LQR", "Q"),
        ("L QR", " "),
    ],
)
def test_parse_instructions_raises_invalidinstructionerror_for_malformed_input(
    input, invalid_character
):
    with pytest.raises(
        InvalidInstructionError,
        match=rf"{re.escape(repr(invalid_character))} is not a valid Instruction",
    ):
        parse_instructions(input)


def test_parse_mission_returns_correct_structure_with_plateau_line_only():
    mock_mission = "5 5"
    expected_result = {"plateau": {"max_x": 5, "max_y": 5}, "rovers": []}

    result = parse_mission(mock_mission)

    assert result == expected_result


def test_parse_mission_returns_correct_structure_with_one_rover_only():
    mock_mission = "5 5\n1 2 N\nLMLMLMLMM"

    expected_result = {
        "plateau": {"max_x": 5, "max_y": 5},
        "rovers": [
            {
                "position": {
                    "x": 1,
                    "y": 2,
                    "direction": CompassDirection.NORTH,
                    "rover_type": RoverType.SCIENCE,
                },
                "instructions": [
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("M"),
                ],
            }
        ],
    }

    result = parse_mission(mock_mission)

    assert result == expected_result


def test_parse_mission_returns_correct_structure_with_newline_at_end_of_input():
    mock_mission = "5 5\n1 2 N\nLMLMLMLMM\n"

    expected_result = {
        "plateau": {"max_x": 5, "max_y": 5},
        "rovers": [
            {
                "position": {
                    "x": 1,
                    "y": 2,
                    "direction": CompassDirection.NORTH,
                    "rover_type": RoverType.SCIENCE,
                },
                "instructions": [
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("M"),
                ],
            }
        ],
    }

    result = parse_mission(mock_mission)

    assert result == expected_result


def test_parse_mission_returns_correct_structure_with_multiple_rovers():
    mock_mission = "5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM"

    expected_result = {
        "plateau": {"max_x": 5, "max_y": 5},
        "rovers": [
            {
                "position": {
                    "x": 1,
                    "y": 2,
                    "direction": CompassDirection.NORTH,
                    "rover_type": RoverType.SCIENCE,
                },
                "instructions": [
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("L"),
                    Instruction("M"),
                    Instruction("M"),
                ],
            },
            {
                "position": {
                    "x": 3,
                    "y": 3,
                    "direction": CompassDirection.EAST,
                    "rover_type": RoverType.SCIENCE,
                },
                "instructions": [
                    Instruction("M"),
                    Instruction("M"),
                    Instruction("R"),
                    Instruction("M"),
                    Instruction("M"),
                    Instruction("R"),
                    Instruction("M"),
                    Instruction("R"),
                    Instruction("R"),
                    Instruction("M"),
                ],
            },
        ],
    }

    result = parse_mission(mock_mission)

    assert result == expected_result


def test_load_mission_from_file_raises_typeerror_for_invalid_path_argument_type():
    with pytest.raises(TypeError, match="Expected type str or Path as path argument"):
        load_mission_from_file(123)  # type: ignore


def test_load_mission_from_file_returns_unchanged_string():
    mock_file_content = "5 5\n1 2 N\nLMLMLMLMM\n3 3 E\nMMRMMRMRRM"

    mock_file = mock_open(read_data=mock_file_content)

    with patch("builtins.open", mock_file):
        result = load_mission_from_file("dummy/path")

    assert result == mock_file_content


def test_argument_type_validator_accepts_multiple_argument_types():
    @argument_type_validator({"name": str, "count": int})
    def describe(name, count):
        return f"{name}:{count}"

    assert describe("rover", 2) == "rover:2"


@pytest.mark.parametrize(
    "name,count,invalid_argument",
    [
        (123, 2, "name"),
        ("rover", "2", "count"),
    ],
)
def test_argument_type_validator_rejects_invalid_argument_types(
    name, count, invalid_argument
):
    @argument_type_validator({"name": str, "count": int})
    def describe(name, count):
        return f"{name}:{count}"

    with pytest.raises(TypeError, match=invalid_argument):
        describe(name, count)


def test_argument_type_validator_supports_keyword_arguments():
    @argument_type_validator({"name": str, "count": int})
    def describe(name, count):
        return f"{name}:{count}"

    assert describe(name="rover", count=2) == "rover:2"


def test_argument_type_validator_preserves_function_metadata():
    @argument_type_validator({"value": str})
    def process(value):
        """Process a value."""
        return value

    assert process.__name__ == "process"
    assert process.__doc__ == "Process a value."


def test_argument_type_validator_ignores_self_argument_when_validating_class_methods():
    class Dummy:
        @argument_type_validator({"dummy_arg": str})
        def __init__(self, dummy_arg):
            self._dummy_arg = dummy_arg

    dummy = Dummy("dummy")

    assert dummy._dummy_arg == "dummy"


@pytest.mark.parametrize("argument", [123, "123"])
def test_argument_type_validator_accepts_argument_with_multiple_valid_data_types(
    argument,
):
    @argument_type_validator({"name": str, "count": (int, str)})
    def dummy_function(name: str, count: int | str):
        return f"Name: {name} | Count: {count!s}"

    result = dummy_function("test", argument)

    assert result == "Name: test | Count: 123"


@pytest.mark.parametrize(
    "value, expected_rover_type", [("S", RoverType.SCIENCE), ("C", RoverType.CARGO)]
)
@patch("src.input_layer.input")
def test_validate_rover_type_from_input_returns_correct_rovertype_when_from_valid_input(
    mock_user_input, value, expected_rover_type
):
    mock_user_input.return_value = value
    rover_type = validate_rover_type_from_input()

    assert rover_type == expected_rover_type


@patch("src.input_layer.input")
def test_validate_rover_type_from_input_returns_none_when_input_is_abort(
    mock_user_input,
):
    mock_user_input.return_value = "abort"
    rover_type = validate_rover_type_from_input()

    assert rover_type is None


@patch("src.input_layer.input")
def test_validate_rover_type_from_input_prints_error_and_prompts_with_invalid_input(
    mock_user_input, capsys
):
    mock_user_input.side_effect = ["A", "S"]

    rover_type = validate_rover_type_from_input()

    output = capsys.readouterr().out
    assert rover_type == RoverType.SCIENCE
    assert "is not a valid RoverType" in output
    assert "Please try entering the rover type again" in output
    assert mock_user_input.call_count == 2


@patch("src.input_layer.input")
def test_validate_instructions_from_input_returns_correct_list_of_instructions_from_valid_input(
    mock_user_input,
):
    mock_user_input.return_value = "LMR"
    expected_instructions = [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]
    instructions = validate_instructions_from_input()

    assert instructions == expected_instructions


@patch("src.input_layer.input")
def test_validate_instructions_from_input_returns_none_when_input_is_abort(
    mock_user_input,
):
    mock_user_input.return_value = "abort"
    instructions = validate_instructions_from_input()

    assert instructions is None


@patch("src.input_layer.input")
def test_validate_instructions_from_input_prints_error_and_prompts_with_invalid_input(
    mock_user_input, capsys
):
    mock_user_input.side_effect = ["LMRN", "LMR"]

    instructions = validate_instructions_from_input()

    output = capsys.readouterr().out
    assert instructions == [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]
    assert "Instructions must be a string with no spaces" in output
    assert "Please try entering the instructions again" in output
    assert mock_user_input.call_count == 2
