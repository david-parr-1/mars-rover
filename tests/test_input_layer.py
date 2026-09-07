from src.input_layer import parse_plateau


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
