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
        self._max_x = max_x
        self._max_y = max_y

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
