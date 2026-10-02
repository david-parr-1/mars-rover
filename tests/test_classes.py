from datetime import datetime, timezone

import pytest

from src.classes import Mission, Plateau, Position, Rover
from src.custom_enums import CompassDirection, Instruction, RoverType
from src.exceptions import (
    InvalidPlateauError,
    InvalidPositionError,
    LoadFromDictError,
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


def test_plateau_eq_returns_true_if_attributes_are_identical_to_another_instance():
    plateau_1 = Plateau(5, 5)
    plateau_2 = Plateau(5, 5)

    assert plateau_1 == plateau_2
    assert plateau_1 is not plateau_2


@pytest.mark.parametrize(
    "comparison_plateau", [Plateau(4, 5), Plateau(5, 4), Plateau(4, 4)]
)
def test_plateau_eq_returns_false_if_attributes_are_not_identical_to_another_instance(
    comparison_plateau,
):
    plateau = Plateau(5, 5)

    assert plateau != comparison_plateau


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


def test_plateau_to_dict_returns_dict_in_expected_format(plateau_class_instance):
    expected_result = {"min_x": 0, "max_x": 1, "min_y": 0, "max_y": 2}

    result = plateau_class_instance.to_dict()

    assert result == expected_result


def test_plateau_from_dict_sets_instance_attributes_successfully():
    parameters = {"max_x": 8, "max_y": 8}
    expected_result = Plateau(8, 8)

    plateau = Plateau.from_dict(parameters)

    assert plateau == expected_result


@pytest.mark.parametrize(
    "parameters",
    [
        {},
        {"max_x": 8},
        {"max_y": 8},
    ],
)
def test_plateau_from_dict_raises_loadfromdicterror_with_missing_parameters(
    parameters,
):
    with pytest.raises(
        LoadFromDictError,
        match=(
            r"^The parameters dictionary passed to Plateau\.from_dict\(\) "
            "is missing"
        ),
    ):
        Plateau.from_dict(parameters)


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


def test_position_to_dict_returns_dict_in_expected_format(position_class_instance):
    expected_result = {"x": 1, "y": 2, "direction": "N"}

    result = position_class_instance.to_dict()

    assert result == expected_result


def test_position_from_dict_sets_instance_attributes_successfully():
    parameters = {"x": 1, "y": 2, "direction": "N"}
    expected_result = Position(1, 2, CompassDirection.NORTH)

    position = Position.from_dict(parameters)

    assert position == expected_result


@pytest.mark.parametrize(
    "parameters",
    [
        {"y": 2, "direction": "N"},
        {"x": 1, "direction": "N"},
        {"x": 1, "y": 2},
        {"x": 1},
        {"y": 2},
        {"direction": "N"},
        {},
    ],
)
def test_position_from_dict_raises_loadfromdicterror_with_missing_parameters(
    parameters,
):
    with pytest.raises(
        LoadFromDictError,
        match=(
            r"^The parameters dictionary passed to Position\.from_dict\(\) "
            "is missing"
        ),
    ):
        Position.from_dict(parameters)


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


def test_rover_init_sets_correct_positions_attributes_when_initialising_with_latest_position_arg(
    rover_class_instance_with_latest_position_arg,
):
    assert rover_class_instance_with_latest_position_arg.start_position == Position(
        1, 2, CompassDirection.NORTH
    )
    assert rover_class_instance_with_latest_position_arg.latest_position == Position(
        3, 4, CompassDirection.EAST
    )


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


def test_rover_from_dict_sets_instance_attributes_successfully(rover_as_dict):
    plateau = Plateau(8, 8)
    expected_result = Rover(
        Position(1, 2, CompassDirection.NORTH),
        [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT],
        plateau,
        RoverType.SCIENCE,
        latest_position=Position(3, 4, CompassDirection.EAST),
    )

    result = Rover.from_dict(rover_as_dict, plateau)

    assert result == expected_result


@pytest.mark.parametrize(
    "parameters",
    [
        {
            "latest_position": {"x": 3, "y": 4, "direction": "E"},
            "instructions": "LMR",
            "rover_type": "S",
        },
        {
            "start_position": {"x": 1, "y": 2, "direction": "N"},
            "instructions": "LMR",
            "rover_type": "S",
        },
        {
            "start_position": {"x": 1, "y": 2, "direction": "N"},
            "latest_position": {"x": 3, "y": 4, "direction": "E"},
            "rover_type": "S",
        },
        {
            "start_position": {"x": 1, "y": 2, "direction": "N"},
            "latest_position": {"x": 3, "y": 4, "direction": "E"},
            "instructions": "LMR",
        },
    ],
)
def test_rover_from_dict_raises_loadfromdict_with_missing_parameters(
    eight_by_eight_plateau_instance, parameters
):
    with pytest.raises(
        LoadFromDictError,
        match=(r"^The parameters dictionary passed to Rover\.from_dict\(\) is missing"),
    ):
        Rover.from_dict(parameters, eight_by_eight_plateau_instance)


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


def test_rover_eq_returns_true_if_attributes_are_identical(plateau_class_instance):
    rover_1 = Rover(
        Position(1, 2, CompassDirection.NORTH), "LMR", plateau_class_instance
    )
    rover_2 = Rover(
        Position(1, 2, CompassDirection.NORTH), "LMR", plateau_class_instance
    )

    assert rover_1 == rover_2
    assert rover_1 is not rover_2


@pytest.mark.parametrize(
    "comparison_rover",
    [
        Rover(Position(2, 2, CompassDirection.NORTH), "LMR", Plateau(5, 5)),
        Rover(Position(1, 3, CompassDirection.NORTH), "LMR", Plateau(5, 5)),
        Rover(Position(1, 2, CompassDirection.EAST), "LMR", Plateau(5, 5)),
        Rover(Position(1, 2, CompassDirection.NORTH), "LMRM", Plateau(5, 5)),
        Rover(
            Position(1, 2, CompassDirection.NORTH),
            "LMR",
            Plateau(5, 5),
            rover_type=RoverType.CARGO,
        ),
    ],
)
def test_rover_eq_returns_false_if_attributes_are_not_identical(comparison_rover):
    rover = Rover(Position(1, 2, CompassDirection.NORTH), "LMR", Plateau(4, 5))

    assert rover != comparison_rover


def test_rover_instructions_to_string_returns_expected_value(
    rover_class_instance_with_list_of_instructions,
):
    expected_result = "LMR"

    result = rover_class_instance_with_list_of_instructions.instructions_to_string()

    assert result == expected_result


def test_rover_to_dict_returns_dict_in_expected_format(
    rover_class_instance_with_list_of_instructions,
):
    expected_result = {
        "start_position": {"x": 1, "y": 2, "direction": "N"},
        "latest_position": {"x": 1, "y": 2, "direction": "N"},
        "instructions": "LMR",
        "rover_type": "S",
    }

    result = rover_class_instance_with_list_of_instructions.to_dict()

    assert result == expected_result


def test_mission_init_sets_expected_default_values():
    mission = Mission()

    assert mission.plateau == None
    assert mission.rovers == []
    assert mission.timestamp == None


def test_mission_init_sets_correct_values_when_argument_supplied(
    plateau_class_instance,
    rover_class_instance_with_list_of_instructions,
    cargo_rover_class_instance,
):
    rovers = [
        rover_class_instance_with_list_of_instructions,
        cargo_rover_class_instance,
    ]
    timestamp = datetime.now(timezone.utc)
    mission = Mission(plateau_class_instance, rovers, timestamp)

    assert mission.plateau == plateau_class_instance
    assert mission.plateau is not plateau_class_instance
    assert mission.rovers == rovers
    assert mission.rovers is not rovers
    assert mission.timestamp == timestamp


def test_mission_add_rover_adds_rover_to_empty_list(
    rover_class_instance_with_list_of_instructions,
):
    mission = Mission()
    expected_result = [rover_class_instance_with_list_of_instructions]

    mission.add_rover(rover_class_instance_with_list_of_instructions)

    assert mission.rovers == expected_result


def test_mission_add_rover_adds_rover_to_non_empty_list(
    rover_class_instance_with_list_of_instructions,
    cargo_rover_class_instance,
    plateau_class_instance,
):
    rovers = [rover_class_instance_with_list_of_instructions]
    mission = Mission(plateau_class_instance, rovers)
    expected_result = [
        rover_class_instance_with_list_of_instructions,
        cargo_rover_class_instance,
    ]

    mission.add_rover(cargo_rover_class_instance)

    assert mission.rovers == expected_result


def test_mission_to_dict_returns_dict_in_expected_format(mission_instance):
    expected_result = {
        "plateau": {"min_x": 0, "max_x": 8, "min_y": 0, "max_y": 8},
        "rovers": [
            {
                "start_position": {"x": 1, "y": 2, "direction": "N"},
                "latest_position": {"x": 1, "y": 2, "direction": "N"},
                "instructions": "LMR",
                "rover_type": "S",
            },
            {
                "start_position": {"x": 1, "y": 2, "direction": "N"},
                "latest_position": {"x": 1, "y": 2, "direction": "N"},
                "instructions": "LMR",
                "rover_type": "C",
            },
        ],
        "timestamp": datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc).isoformat(),
    }

    result = mission_instance.to_dict()

    assert result == expected_result


def test_mission_eq_returns_true_if_attributes_are_identical(
    mission_instance, mission_instance_identical
):
    assert mission_instance is not mission_instance_identical
    assert mission_instance == mission_instance_identical


@pytest.mark.parametrize(
    "non_identical_mission_instance",
    [
        "mission_instance_different_plateau",
        "mission_instance_different_rovers",
        "mission_instance_different_timestamp",
    ],
)
def test_mission_eq_returns_false_if_attributes_are_not_identical(
    request, mission_instance, non_identical_mission_instance
):
    non_identical_mission_instance = request.getfixturevalue(
        non_identical_mission_instance
    )
    assert mission_instance != non_identical_mission_instance


def test_mission_from_dict_sets_instance_attributes_successfully(
    eight_by_eight_plateau_instance, mission_as_dict
):
    expected_result = Mission(
        eight_by_eight_plateau_instance,
        [
            Rover(
                Position(1, 2, CompassDirection.NORTH),
                [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT],
                eight_by_eight_plateau_instance,
                RoverType.SCIENCE,
                Position(3, 4, CompassDirection.EAST),
            ),
            Rover(
                Position(5, 6, CompassDirection.SOUTH),
                [Instruction.RIGHT, Instruction.MOVE, Instruction.LEFT],
                eight_by_eight_plateau_instance,
                RoverType.CARGO,
                Position(7, 8, CompassDirection.WEST),
            ),
        ],
        datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )

    result = Mission.from_dict(mission_as_dict)

    assert result == expected_result


@pytest.mark.parametrize(
    "mission_dict_with_missing_parameter",
    [
        "mission_as_dict_no_plateau",
        "mission_as_dict_no_rovers",
        "mission_as_dict_no_timestamp",
    ],
)
def test_mission_from_dict_raises_loadfromdicterror_with_missing_parameters(
    request, mission_dict_with_missing_parameter
):
    malformed_mission_dict = request.getfixturevalue(
        mission_dict_with_missing_parameter
    )
    with pytest.raises(
        LoadFromDictError,
        match=(
            r"^The parameters dictionary passed to Mission\.from_dict\(\) is missing"
        ),
    ):
        Mission.from_dict(malformed_mission_dict)
