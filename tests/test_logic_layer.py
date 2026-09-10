import pytest

from src.logic_layer import rotate


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
