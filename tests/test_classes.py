from src.custom_enums import CompassDirection


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
