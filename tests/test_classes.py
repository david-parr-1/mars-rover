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
