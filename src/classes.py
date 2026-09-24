from copy import deepcopy

from src.custom_enums import CompassDirection, Instruction
from src.exceptions import (
    InvalidPlateauError,
    InvalidPositionError,
)
from src.input_layer import argument_type_validator, parse_instructions
from src.logic_layer import MOVEMENTS, ROTATIONS, get_logger

logger = get_logger(__name__)


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
        logger.info("Initialising plateau...")
        self.max_x = max_x
        self.max_y = max_y
        logger.info(
            f"Plateau initialised successfully. max_x: {self.max_x} | "
            f"max_y: {self.max_y}"
        )

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

        Raises:
            `InvalidPlateauError` if a value of 0 or less is passed.
        """
        if value <= 0:
            raise InvalidPlateauError(
                f"Plateau max_x value must be greater than 0. Got {value}"
            )

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

        Raises:
            `InvalidPlateauError` if a value of 0 or less is passed.
        """
        if value <= 0:
            raise InvalidPlateauError(
                f"Plateau max_y value must be greater than 0. Got {value}"
            )

        self._max_y = value

    def __repr__(self) -> str:
        plateau_dims = {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
        }

        return str(plateau_dims)


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

        Raises:
            `InvalidPositionError` if a negative value is passed.
        """
        if value < 0:
            raise InvalidPositionError(f"The x value cannot be negative. Got {value}")

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

        Raises:
            `InvalidPositionError` if a negative value is passed.
        """
        if value < 0:
            raise InvalidPositionError(f"The y value cannot be negative. Got {value}")

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
    def __init__(
        self,
        start_position: Position,
        instructions: str | list[Instruction],
        plateau: Plateau,
    ) -> None:
        logger.info("Initialising rover...")

        # It is necessary to validate the rover's start_position in relation to the mission
        # plateau to ensure that a rover doesn't have an "impossible" position i.e. a
        # position outside of the mission's bound as defined by the plateau's x and y
        # attributes. NOTE:- Validation that a position does not have negative x or y
        # values is executed by the Position() class' __init__ method.
        if not (
            start_position.x <= plateau.max_x and start_position.y <= plateau.max_y
        ):
            logger.error(
                f"Rover could not be initialised as its start position is outside "
                f"of the plateau's bounds. Rover start_position: {start_position} | "
                f"Plateau dimensions: {plateau}"
            )
            raise InvalidPositionError(
                f"A rover's start_position must be within the mission plateau's "
                f"min and max x and y attributes.\n"
                f"Plateau attributes are: {plateau}\n"
                f"Rover start_position is: {start_position}"
            )

        self.start_position = start_position
        self.latest_position = deepcopy(start_position)
        self.instructions = instructions
        logger.info(
            f"Successfully initialised rover. start_position: {self.start_position} | "
            f"instructions: {self.instructions}"
        )

    @property
    def start_position(self) -> Position:
        return self._start_position

    @start_position.setter
    @argument_type_validator({"position": Position})
    def start_position(self, position: Position) -> None:
        self._start_position = position

    @property
    def instructions(self) -> list[Instruction]:
        return self._instructions

    @instructions.setter
    @argument_type_validator({"instructions": (str, list)})
    def instructions(self, instructions: str | list[Instruction]) -> None:
        if isinstance(instructions, str):
            self._instructions = parse_instructions(instructions)
        else:
            self._instructions = instructions

    @property
    def latest_position(self) -> Position:
        return self._latest_position

    @latest_position.setter
    @argument_type_validator({"position": Position})
    def latest_position(self, position: Position) -> None:
        self._latest_position = position

    @argument_type_validator({"plateau": Plateau})
    def _move(self, plateau: Plateau) -> Position:
        initial_position = repr(self.latest_position)
        logger.info(f"Moving rover at position: {initial_position}")
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
            logger.info(
                f"Rover move complete. Position was: {initial_position} | "
                f"New position is: {self.latest_position}"
            )
            return self.latest_position
        else:
            logger.warning(
                f"Rover at position {initial_position} has reached the edge "
                f"of the plateau. Position remains unchanged at {self.latest_position}"
            )
            return self.latest_position

    @argument_type_validator({"instruction": Instruction})
    def _rotate(self, instruction: Instruction) -> Position:
        initial_position = repr(self.latest_position)
        logger.info(f"Rotating rover at {initial_position}...")
        rotated_direction = ROTATIONS[self.latest_position.direction][instruction]
        self.latest_position.direction = rotated_direction
        logger.info(
            f"Rover rotation completed successfully for rover at {initial_position}. "
            f"New position is: {self.latest_position}"
        )

        return self.latest_position

    @argument_type_validator({"plateau": Plateau})
    def execute_instructions(
        self,
        plateau: Plateau,
    ) -> Position:
        initial_position = repr(self.latest_position)
        logger.info(
            f"Beginning execution of instructions for rover at {initial_position} with "
            f"instructions: {self.instructions}"
        )
        for instruction in self.instructions:
            if instruction == Instruction.MOVE:
                updated_rover_position = self._move(plateau)
                self.latest_position = updated_rover_position
            else:
                updated_rover_position = self._rotate(instruction)
                self.latest_position = updated_rover_position

        logger.info(
            f"Completed execution of instructions. Final rover position: "
            f"{self.latest_position}"
        )

        return self.latest_position
