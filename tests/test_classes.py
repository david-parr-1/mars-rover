import pytest

from src.classes import Plateau, Position, Rover
from src.custom_enums import CompassDirection, Instruction, RoverType
from src.exceptions import (
    InvalidPlateauError,
    InvalidPositionError,
)


def test_plateau_init_returns_expected_values(plateau_class_instance):
    assert plateau_class_instance.min_x == 0, (
        "Plateau() class initialissed with incorrect min_x value"
    )
    assert plateau_class_instance.min_y == 0, (
        "Plateau() class initialissed with incorrect min_y value"
    )
    assert plateau_class_instance.max_x == 1, (
        "Plateau() class initialised with incorrect max_x value"
    )
    assert plateau_class_instance.max_y == 2, (
        "Plateau() class initialised with incorrect max_y value"
    )


def test_plateau_repr_formats_correctly(plateau_class_instance):
    expected_result = str({"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 2})

    assert repr(plateau_class_instance) == expected_result


@pytest.mark.parametrize("max_x", [-1, 0])
def test_plateau_init_raises_invalidplateauerror_with_non_positive_max_x_values(max_x):
    with pytest.raises(
        InvalidPlateauError, match="Plateau max_x value must be greater than 0"
    ):
        Plateau(max_x, 1)


@pytest.mark.parametrize("max_y", [-1, 0])
def test_plateau_init_raises_invalidplateauerror_with_non_positive_max_y_values(max_y):
    with pytest.raises(
        InvalidPlateauError, match="Plateau max_y value must be greater than 0"
    ):
        Plateau(1, max_y)


def test_position_init_returns_expected_values(position_class_instance):
    assert position_class_instance.x == 1, (
        "Position() class initialissed with incorrect x value"
    )
    assert position_class_instance.y == 2, (
        "Position() class initialissed with incorrect y value"
    )
    assert position_class_instance.direction == CompassDirection.NORTH, (
        "Position() class initialised with incorrect direction value"
    )


def test_position_init_raises_invalidpositionerror_if_x_lt_0():
    with pytest.raises(InvalidPositionError, match="The x value cannot be negative"):
        Position(-1, 1, CompassDirection.NORTH)


def test_position_init_raises_invalidpositionerror_if_y_lt_0():
    with pytest.raises(InvalidPositionError, match="The y value cannot be negative"):
        Position(1, -1, CompassDirection.NORTH)


def test_position_init_successful_when_x_and_y_eq_0():
    position = Position(0, 0, CompassDirection.NORTH)

    assert position.x == 0
    assert position.y == 0
    assert position.direction == CompassDirection.NORTH


@pytest.mark.parametrize(
    "other_position_class_instance,expected_result",
    [
        (Position(1, 2, CompassDirection.NORTH), True),
        (Position(2, 2, CompassDirection.NORTH), False),
        (Position(1, 3, CompassDirection.NORTH), False),
        (Position(1, 2, CompassDirection.EAST), False),
        (Position(2, 3, CompassDirection.NORTH), False),
        (Position(1, 3, CompassDirection.EAST), False),
        (Position(2, 2, CompassDirection.EAST), False),
        (Position(2, 3, CompassDirection.EAST), False),
    ],
)
def test_position_returns_false_if_attributes_not_eq_to_another_position_instance(
    position_class_instance, other_position_class_instance, expected_result
):
    result = position_class_instance == other_position_class_instance

    assert result == expected_result


def test_position_repr_formats_correctly(position_class_instance):
    expected_result = "{{x: 1, y: 2, direction: CompassDirection.NORTH}}".format()
    assert repr(position_class_instance) == expected_result


def test_rover_init_with_instructions_string_returns_expected_values(
    rover_class_instance,
):
    assert rover_class_instance.start_position == Position(
        1, 2, CompassDirection.NORTH
    ), "Rover() class initialised with incorrect start_position value"
    assert rover_class_instance.instructions == [
        Instruction.LEFT,
        Instruction.MOVE,
        Instruction.RIGHT,
    ], "Rover() class initialised with incorrect instructions value"


def test_rover_init_with_list_of_instructions_returns_expected_values(
    rover_class_instance_with_list_of_instructions,
):
    assert rover_class_instance_with_list_of_instructions.start_position == Position(
        1, 2, CompassDirection.NORTH
    ), "Rover() class initialised with incorrect start_position value"
    assert rover_class_instance_with_list_of_instructions.instructions == [
        Instruction.LEFT,
        Instruction.MOVE,
        Instruction.RIGHT,
    ], "Rover() class initialised with incorrect instructions value"


def test_rover_init_sets_correct_attribute_values_with_default_rover_type(
    rover_class_instance,
):
    assert rover_class_instance.rover_type == RoverType.SCIENCE
    assert rover_class_instance.movement_speed == 1


def test_rover_init_sets_correct_attribute_values_with_cargo_rover_type(
    cargo_rover_class_instance,
):
    assert cargo_rover_class_instance.rover_type == RoverType.CARGO
    assert cargo_rover_class_instance.movement_speed == 2


@pytest.mark.parametrize(
    "plateau,start_position",
    [
        (Plateau(1, 2), Position(2, 2, CompassDirection.NORTH)),
        (Plateau(1, 2), Position(1, 3, CompassDirection.NORTH)),
        (Plateau(1, 2), Position(2, 3, CompassDirection.NORTH)),
        (Plateau(5, 5), Position(6, 5, CompassDirection.NORTH)),
        (Plateau(5, 5), Position(5, 6, CompassDirection.NORTH)),
        (Plateau(5, 5), Position(6, 6, CompassDirection.NORTH)),
    ],
)
def test_rover_init_raises_invalidpositionerror_with_start_position_outside_plateau_bounds(
    plateau, start_position
):
    with pytest.raises(
        InvalidPositionError,
        match=(
            "A rover's start_position must be within the mission plateau's min and max x and "
            "y attributes"
        ),
    ):
        Rover(start_position, "LMR", plateau)


@pytest.mark.parametrize(
    "instructions", ["LMR", [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]]
)
def test_rover_instructions_setter_accepts_instruction_string_or_list(instructions):
    plateau = Plateau(5, 5)
    rover = Rover(Position(1, 2, CompassDirection.NORTH), instructions, plateau)

    assert rover.instructions == [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]


def test_rover_move_updates_rover_latest_position_attribute():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "LMR", plateau)

    mock_rover._move(plateau)

    assert mock_rover.latest_position == Position(1, 3, CompassDirection.NORTH)


def test_rover_move_does_not_modify_start_position():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "LMR", plateau)

    mock_rover._move(plateau)

    assert mock_rover.latest_position == Position(1, 3, CompassDirection.NORTH)
    assert mock_rover.start_position == Position(1, 2, CompassDirection.NORTH)


@pytest.mark.parametrize(
    "start_position,expected_new_position",
    [
        (
            Position(1, 2, CompassDirection.NORTH),
            Position(1, 3, CompassDirection.NORTH),
        ),
        (Position(1, 2, CompassDirection.EAST), Position(2, 2, CompassDirection.EAST)),
        (
            Position(1, 2, CompassDirection.SOUTH),
            Position(1, 1, CompassDirection.SOUTH),
        ),
        (Position(1, 2, CompassDirection.WEST), Position(0, 2, CompassDirection.WEST)),
    ],
)
def test_rover_move_returns_correct_position_updates(
    start_position, expected_new_position
):
    plateau = Plateau(5, 5)
    rover = Rover(start_position, "LMR", plateau)

    result = rover._move(plateau)

    assert result == expected_new_position


@pytest.mark.parametrize(
    "start_position",
    [
        (Position(5, 5, CompassDirection.NORTH)),
        (Position(5, 5, CompassDirection.EAST)),
        (Position(0, 0, CompassDirection.SOUTH)),
        (Position(0, 0, CompassDirection.WEST)),
    ],
)
def test_rover_move_returns_unchanged_position_at_plateau_edges(start_position):
    plateau = Plateau(5, 5)
    rover = Rover(start_position, "LMR", plateau)

    result = rover._move(plateau)

    assert result == rover.start_position


@pytest.mark.parametrize(
    "start_position,expected_position",
    [
        (
            Position(3, 3, CompassDirection.NORTH),
            Position(3, 5, CompassDirection.NORTH),
        ),
        (Position(3, 3, CompassDirection.EAST), Position(5, 3, CompassDirection.EAST)),
        (
            Position(3, 3, CompassDirection.SOUTH),
            Position(3, 1, CompassDirection.SOUTH),
        ),
        (Position(3, 3, CompassDirection.WEST), Position(1, 3, CompassDirection.WEST)),
    ],
)
def test_rover_move_moves_2_spaces_for_cargo_rover_type(
    start_position, expected_position
):
    plateau = Plateau(5, 5)
    rover = Rover(start_position, "LMR", plateau, RoverType.CARGO)

    result = rover._move(plateau)

    assert result == expected_position
    assert rover.latest_position == expected_position


@pytest.mark.parametrize(
    "start_position",
    [
        Position(3, 4, CompassDirection.NORTH),
        Position(4, 3, CompassDirection.EAST),
        Position(3, 1, CompassDirection.SOUTH),
        Position(1, 3, CompassDirection.WEST),
    ],
)
def test_rover_move_returns_unchanged_position_at_plateau_edge_for_cargo_rover(
    start_position,
):
    plateau = Plateau(5, 5)
    rover = Rover(start_position, "LMR", plateau, RoverType.CARGO)

    result = rover._move(plateau)

    assert result is not start_position
    assert result == start_position
    assert rover.latest_position is not start_position
    assert rover.latest_position == start_position


def test_rover_rotate_updates_rover_latest_position_attribute():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "LMR", plateau)

    mock_rover._rotate(Instruction.RIGHT)

    assert mock_rover.latest_position == Position(1, 2, CompassDirection.EAST)


def test_rover_rotate_does_not_modify_start_position():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "LMR", plateau)

    mock_rover._rotate(Instruction.RIGHT)

    assert mock_rover.start_position == Position(1, 2, CompassDirection.NORTH)
    assert mock_rover.latest_position == Position(1, 2, CompassDirection.EAST)


@pytest.mark.parametrize(
    "start_direction,instruction,expected_direction",
    [
        (CompassDirection.NORTH, Instruction.LEFT, CompassDirection.WEST),
        (CompassDirection.NORTH, Instruction.RIGHT, CompassDirection.EAST),
        (CompassDirection.EAST, Instruction.LEFT, CompassDirection.NORTH),
        (CompassDirection.EAST, Instruction.RIGHT, CompassDirection.SOUTH),
        (CompassDirection.SOUTH, Instruction.LEFT, CompassDirection.EAST),
        (CompassDirection.SOUTH, Instruction.RIGHT, CompassDirection.WEST),
        (CompassDirection.WEST, Instruction.LEFT, CompassDirection.SOUTH),
        (CompassDirection.WEST, Instruction.RIGHT, CompassDirection.NORTH),
    ],
)
def test_rover_rotate_returns_correct_direction(
    start_direction, instruction, expected_direction
):
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, start_direction), "LMR", plateau)

    rotated_rover = mock_rover._rotate(instruction)

    assert rotated_rover == Position(1, 2, expected_direction)


def test_rover_execute_instructions_returns_unchanged_position_for_empty_instruction_list():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "", plateau)

    moved_rover = mock_rover.execute_instructions(plateau)

    assert moved_rover == mock_rover.start_position


def test_rover_execute_instructions_returns_correct_position_for_single_instruction_list():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "M", plateau)

    moved_rover = mock_rover.execute_instructions(plateau)

    assert moved_rover == Position(1, 3, CompassDirection.NORTH)


def test_rover_execute_instructions_returns_correct_position_for_multi_instruction_list():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "MRMRML", plateau)

    moved_rover = mock_rover.execute_instructions(plateau)

    assert moved_rover == Position(2, 2, CompassDirection.EAST)


def test_rover_execute_instructions_updates_rover_latest_position_attribute():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "MRMRML", plateau)

    mock_rover.execute_instructions(plateau)

    assert mock_rover.latest_position == Position(2, 2, CompassDirection.EAST)


def test_rover_execute_instructions_does_not_modify_rover_start_position():
    plateau = Plateau(5, 5)
    mock_rover = Rover(Position(1, 2, CompassDirection.NORTH), "MRMRML", plateau)

    mock_rover.execute_instructions(plateau)

    assert mock_rover.start_position == Position(1, 2, CompassDirection.NORTH)
    assert mock_rover.latest_position == Position(2, 2, CompassDirection.EAST)
