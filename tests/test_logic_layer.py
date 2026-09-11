import pytest

from src.logic_layer import execute_instructions, move, rotate


@pytest.mark.parametrize(
    "start_direction,instruction,expected_direction",
    [
        ("N", "L", "W"),
        ("N", "R", "E"),
        ("E", "L", "N"),
        ("E", "R", "S"),
        ("S", "L", "E"),
        ("S", "R", "W"),
        ("W", "L", "S"),
        ("W", "R", "N"),
    ],
)
def test_rotate_returns_correct_rotation(
    start_direction, instruction, expected_direction
):
    mock_position = {"x": 1, "y": 2, "direction": start_direction}

    expected_result = {**mock_position, "direction": expected_direction}

    result = rotate(mock_position, instruction)

    assert result == expected_result


def test_rotate_returns_new_dictionary():
    mock_position = {"x": 1, "y": 2, "direction": "N"}

    result = rotate(mock_position, "L")

    assert result is not mock_position


@pytest.mark.parametrize("direction", [1, 1.0, [1], {"1": 1}, {1}, (1,)])
def test_rotate_raises_typeerror_if_direction_not_str(direction):
    mock_position = {"x": 1, "y": 2, "direction": direction}

    with pytest.raises(
        TypeError,
        match="The `direction` value of the position dictionary must be a string",
    ):
        rotate(mock_position, "L")


@pytest.mark.parametrize(
    "start_direction,start_x,start_y,end_direction,end_x,end_y",
    [
        ("N", 1, 1, "N", 1, 2),
        ("E", 1, 1, "E", 2, 1),
        ("S", 1, 1, "S", 1, 0),
        ("W", 1, 1, "W", 0, 1),
    ],
)
def test_move_returns_correct_position_updates(
    start_direction, start_x, start_y, end_direction, end_x, end_y
):
    mock_position = {"x": start_x, "y": start_y, "direction": start_direction}

    mock_plateau = {"max_x": 5, "max_y": 5}

    expected_result = {"x": end_x, "y": end_y, "direction": end_direction}

    result = move(mock_position, mock_plateau)

    assert result == expected_result


@pytest.mark.parametrize(
    "start_direction,start_x,start_y",
    [("N", 1, 5), ("E", 5, 1), ("S", 1, 0), ("W", 0, 1)],
)
def test_move_returns_unchanged_positions_at_plateau_edges(
    start_direction, start_x, start_y
):
    mock_position = {"x": start_x, "y": start_y, "direction": start_direction}

    mock_plateau = {"max_x": 5, "max_y": 5}

    expected_result = {"x": start_x, "y": start_y, "direction": start_direction}

    result = move(mock_position, mock_plateau)

    assert result == expected_result


def test_move_returns_new_dictionary_when_position_is_updated():
    mock_position = {"x": 1, "y": 1, "direction": "N"}

    mock_plateau = {"max_x": 5, "max_y": 5}

    expected_result = {"x": 1, "y": 2, "direction": "N"}

    result = move(mock_position, mock_plateau)

    assert result == expected_result
    assert result is not mock_position


def test_move_returns_new_dictionary_when_position_is_not_updated():
    mock_position = {"x": 1, "y": 5, "direction": "N"}

    mock_plateau = {"max_x": 5, "max_y": 5}

    expected_result = {"x": 1, "y": 5, "direction": "N"}

    result = move(mock_position, mock_plateau)

    assert result == expected_result
    assert result is not mock_position


@pytest.mark.parametrize("x", ["1", 1.0, [1], {"1": 1}, {1}, (1,)])
def test_move_raises_typeerror_if_position_x_not_int(x):
    mock_position = {"x": x, "y": 2, "direction": "N"}

    mock_plateau = {"max_x": 5, "max_y": 5}

    with pytest.raises(
        TypeError,
        match="The `x` value of the position dictionary must be an integer",
    ):
        move(mock_position, mock_plateau)


@pytest.mark.parametrize("y", ["1", 1.0, [1], {"1": 1}, {1}, (1,)])
def test_move_raises_typeerror_if_position_y_not_int(y):
    mock_position = {"x": 1, "y": y, "direction": "N"}

    mock_plateau = {"max_x": 5, "max_y": 5}

    with pytest.raises(
        TypeError,
        match="The `y` value of the position dictionary must be an integer",
    ):
        move(mock_position, mock_plateau)


@pytest.mark.parametrize("direction", [1, 1.0, [1], {"1": 1}, {1}, (1,)])
def test_move_raises_typeerror_if_direction_not_str(direction):
    mock_position = {"x": 1, "y": 1, "direction": direction}

    mock_plateau = {"max_x": 5, "max_y": 5}

    with pytest.raises(
        TypeError,
        match="The `direction` value of the position dictionary must be a string",
    ):
        move(mock_position, mock_plateau)


def test_execute_instructions_returns_unchanged_position_for_empty_instructions_list():
    mock_position = {"x": 1, "y": 2, "direction": "N"}
    mock_instructions = []
    mock_plateau = {"max_x": 5, "max_y": 5}

    result = execute_instructions(mock_position, mock_instructions, mock_plateau)

    assert result == mock_position


@pytest.mark.parametrize(
    "instructions,expected_position",
    [
        ("L", {"x": 1, "y": 2, "direction": "W"}),
        ("R", {"x": 1, "y": 2, "direction": "E"}),
        ("M", {"x": 1, "y": 3, "direction": "N"}),
    ],
)
def test_execute_instructions_returns_correct_position_for_single_instruction_list(
    instructions, expected_position
):
    mock_position = {"x": 1, "y": 2, "direction": "N"}
    mock_plateau = {"max_x": 5, "max_y": 5}

    expected_result = {
        "x": expected_position["x"],
        "y": expected_position["y"],
        "direction": expected_position["direction"],
    }

    result = execute_instructions(mock_position, instructions, mock_plateau)

    assert result == expected_result


def test_execute_instructions_returns_correct_position_for_multi_instruction_list():
    mock_position = {"x": 1, "y": 2, "direction": "N"}
    mock_instructions = ["L", "M", "L", "M", "L", "M", "L", "M", "M"]
    mock_plateau = {"max_x": 5, "max_y": 5}

    expected_result = {"x": 1, "y": 3, "direction": "N"}

    result = execute_instructions(mock_position, mock_instructions, mock_plateau)

    assert result == expected_result


def test_execute_instructions_does_not_mutate_starting_position():
    mock_position = {"x": 1, "y": 2, "direction": "N"}
    mock_instructions = ["L", "M", "L", "M", "L", "M", "L", "M", "M"]
    mock_plateau = {"max_x": 5, "max_y": 5}

    result = execute_instructions(mock_position, mock_instructions, mock_plateau)

    assert result is not mock_position
    assert mock_position == {"x": 1, "y": 2, "direction": "N"}
