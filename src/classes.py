from copy import deepcopy

from src.custom_enums import CompassDirection, Instruction
from src.input_layer import argument_type_validator, parse_instructions
from src.logic_layer import MOVEMENTS, ROTATIONS


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

    def __repr__(self) -> str:
        return f"{{x: {self.x}, y: {self.y}, direction: {self.direction}}}"


class Rover:
    def __init__(self, start_position: Position, instructions: str) -> None:
        self.start_position = start_position
        self.latest_position = deepcopy(start_position)
        self.instructions = instructions

    @property
    def start_position(self) -> Position:
        return self._start_position

    @start_position.setter
    def start_position(self, position: Position) -> None:
        self._start_position = position

    @property
    def instructions(self) -> list[Instruction]:
        return self._instructions

    @instructions.setter
    def instructions(self, instructions: str) -> None:
        self._instructions = parse_instructions(instructions)

    @property
    def latest_position(self) -> Position:
        return self._latest_position

    @latest_position.setter
    def latest_position(self, position: Position) -> None:
        self._latest_position = position

    def _move(self, plateau: Plateau) -> Position:
        start_x = self.latest_position.x
        new_x = start_x + MOVEMENTS[self.latest_position.direction]["x_change"]
        start_y = self.latest_position.y
        new_y = start_y + MOVEMENTS[self.latest_position.direction]["y_change"]

        if (
            plateau.min_x <= new_x <= plateau.max_x
            and plateau.min_y <= new_y <= plateau.max_y
        ):
            self.latest_position.x = new_x
            self.latest_position.y = new_y
            return self.latest_position
        else:
            return self.latest_position

    def _rotate(self, instruction: Instruction) -> Position:
        rotated_direction = ROTATIONS[self.latest_position.direction][instruction]
        self.latest_position.direction = rotated_direction

        return self.latest_position

    def execute_instructions(
        self,
        plateau: Plateau,
    ) -> Position:
        for instruction in self.instructions:
            if instruction == Instruction.MOVE:
                updated_rover_position = self._move(plateau)
                self.latest_position = updated_rover_position
            else:
                updated_rover_position = self._rotate(instruction)
                self.latest_position = updated_rover_position

        return self.latest_position
