from src.custom_enums import CompassDirection
from src.input_layer import argument_type_validator


class Plateau:
    @argument_type_validator({"max_x": int, "max_y": int})
    def __init__(self, max_x: int, max_y: int) -> None:
        """
        Class object representing the mission grid plateau with the
        properties:
            `min_x`
            `min_y`
            `max_x`
            `max_y`

        The `min_x` and `min_y` properties are both set to 0 at class initialisation
        and cannot be modified.

        The `max_x` and `max_y` properties are set at class initialisation but
        can be modified after initialisation.
        """
        self.max_x = max_x
        self.max_y = max_y

    @property
    def min_x(self) -> int:
        """
        Returns the minimum x value of the mission grid plateau which is
        fixed at 0
        """
        return 0

    @property
    def max_x(self) -> int:
        """
        Returns the maximum x value of the mission grid plateau.
        """
        return self._max_x

    @max_x.setter
    @argument_type_validator({"value": int})
    def max_x(self, value: int) -> None:
        """
        Sets the maximum x value of the mission grid plateau.
        """
        self._max_x = value

    @property
    def min_y(self) -> int:
        """
        Returns the minimum y value of the mission grid plateau which is
        fixed at 0
        """
        return 0

    @property
    def max_y(self) -> int:
        """
        Returns the maximum y value of the mission grid plateau.
        """
        return self._max_y

    @max_y.setter
    @argument_type_validator({"value": int})
    def max_y(self, value: int) -> None:
        """
        Sets the maximum y value of the mission grid plateau.
        """
        self._max_y = value


class Position:
    def __init__(self, x: int, y: int, direction: CompassDirection) -> None:
        self.x = x
        self.y = y
        self.direction = direction

    @property
    def x(self) -> int:
        """
        Returns the position's `x` value as an integer.
        """
        return self._x

    @x.setter
    @argument_type_validator({"value": int})
    def x(self, value: int) -> None:
        """
        Sets the position's `x` value as an integer.
        """
        self._x = value

    @property
    def y(self) -> int:
        """
        Returns the position's `y` value as an integer.
        """
        return self._y

    @y.setter
    @argument_type_validator({"value": int})
    def y(self, value: int) -> None:
        """
        Sets the position's `y` value as an integer.
        """
        self._y = value

    @property
    def direction(self) -> CompassDirection:
        """
        Returns the position's direction as an instance of the CompassDirection enum class.
        """
        return self._direction

    @direction.setter
    @argument_type_validator({"value": CompassDirection})
    def direction(self, value: CompassDirection) -> None:
        """
        Sets the position's `direction` as an instance of the CompassDirection enum class.
        """
        self._direction = value

    def __eq__(self, other) -> None:
        return (
            self.x == other.x
            and self.y == other.y
            and self.direction == other.direction
        )
