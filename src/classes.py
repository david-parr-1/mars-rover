import json
import os
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.custom_enums import CompassDirection, Instruction, RoverType
from src.exceptions import (
    InvalidPlateauError,
    InvalidPositionError,
    LoadFromDictError,
)
from src.input_layer import (
    argument_type_validator,
    parse_instructions,
    parse_plateau,
    parse_position,
)
from src.logic_layer import MOVEMENT_SPEED, MOVEMENTS, ROTATIONS, get_logger
from src.text_colours import BLUE_BOLD, BOLD, GREEN_BOLD, ORANGE_BOLD, RESET

logger = get_logger(__name__)


class Plateau:
    """
    Represent the rectangular grid on which rovers operate.

    The minimum coordinates are fixed at zero. The maximum coordinates are
    set during initialization and can be changed afterward, but must remain
    positive.

    Attributes:
        max_x: The maximum x-coordinate of the plateau.
        max_y: The maximum y-coordinate of the plateau.
    """

    @argument_type_validator({"max_x": int, "max_y": int})
    def __init__(self, max_x: int, max_y: int) -> None:
        """
        Initialize the plateau dimensions.

        Args:
            max_x: The positive maximum x-coordinate.
            max_y: The positive maximum y-coordinate.

        Raises:
            InvalidPlateauError: If either dimension is not positive.
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
        fixed at `0`.
        """
        return 0

    @property
    def max_x(self) -> int:
        """
        The maximum `x` coordinate of the `Plateau`.

        The value must be greater than `0`.
        """
        return self._max_x

    @max_x.setter
    @argument_type_validator({"value": int})
    def max_x(self, value: int) -> None:
        """
        Set the maximum `x` value of the `Plateau`.

        Args:
            value: The positive maximum x-coordinate.

        Raises:
            InvalidPlateauError: if a value of `0` or less is passed.
        """
        if value <= 0:
            err_msg = f"Plateau max_x value must be greater than 0. Got {value}"
            logger.error(err_msg)
            raise InvalidPlateauError(err_msg)

        self._max_x = value

    @property
    def min_y(self) -> int:
        """
        Returns the minimum y value of the mission grid plateau which is
        fixed at `0`.
        """
        return 0

    @property
    def max_y(self) -> int:
        """
        Returns the maximum `y` value of the `Plateau`.

        The maximum `y` value must be greater than `0`.
        """
        return self._max_y

    @max_y.setter
    @argument_type_validator({"value": int})
    def max_y(self, value: int) -> None:
        """
        Sets the maximum `y` value of the mission grid plateau.

        Args:
            value: The positive maximum y-coordinate.

        Raises:
            InvalidPlateauError: if a value of `0` or less is passed.
        """
        if value <= 0:
            err_msg = f"Plateau max_y value must be greater than 0. Got {value}"
            logger.error(err_msg)
            raise InvalidPlateauError(err_msg)

        self._max_y = value

    def __repr__(self) -> str:
        plateau_dims = {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
        }

        return str(plateau_dims)

    def __eq__(self, other) -> bool:
        return (
            self.min_x == other.min_x
            and self.max_x == other.max_x
            and self.min_y == other.min_y
            and self.max_y == other.max_y
        )

    def to_dict(self) -> dict[str, Any]:
        """Return this class instance as a dictionary."""
        return {
            "min_x": self.min_x,
            "max_x": self.max_x,
            "min_y": self.min_y,
            "max_y": self.max_y,
        }

    @classmethod
    @argument_type_validator({"parameters": dict})
    def from_dict(cls, parameters: dict[str, int]) -> "Plateau":
        """
        Construct a `Plateau` instance from a dictionary.

        Args:
            parameters: A dictionary containing the required parameters
                to instantiate a `Plateau` object. The required keys are
                `max_x` and `max_y`. Both keys must have positive integer
                values.

        Returns:
            An instance of the `Plateau` class with `max_x` and `max_y`
                attributes mapped to the dictionary passed to the method.

        Raises:
            LoadFromDictError: When the `dict` passed to `parameters` does
                not contain all of the required keys.

        Examples:
            >>> plateau_dict = {'max_x': 4, 'max_y': 6}
            >>> plateau = Plateau.from_dict(plateau_dict)
            >>> plateau.max_x
            4
            >>> plateau.max_y
            6

        """
        reqd_keys = ["max_x", "max_y"]
        for reqd_key in reqd_keys:
            if reqd_key not in parameters:
                err_msg = (
                    f"The parameters dictionary passed to Plateau.from_dict() "
                    f"is missing the {reqd_key} parameter"
                )
                logger.error(err_msg)
                raise LoadFromDictError(err_msg)

        return cls(parameters["max_x"], parameters["max_y"])

    @classmethod
    def from_input(cls) -> "Plateau | None":
        """
        Construct a `Plateau` instance from user prompting.

        If the user enters an invalid response an error message is printed and the user
        is prompted again for input.

        `'abort'` can be entered as a user response which will cause this function to
        return `None` which allows the `mission_cli` to abort mission loading.

        Returns:
            An instance of `Plateau` if user enters valid response. `None` if user
            response is `'abort'`.
        """
        valid_plateau = False
        while not valid_plateau:
            user_input = input(
                f"To begin processing a mission, enter the maximum x and y dimensions "
                f"of the mission's plateau as integers separated by a space e.g. 8 8\n\n"
                f"NOTE:- the value of the x and y dimensions must be greater than 0 and "
                f"no greater than 99.\n\n"
                f"{BLUE_BOLD}Enter the mission plateau dimensions: {RESET}"
            )
            if user_input == "abort":
                print("Aborting mission loading...")
                return None
            try:
                plateau_dims = parse_plateau(user_input)
                max_x, max_y = plateau_dims["max_x"], plateau_dims["max_y"]
                plateau = cls(max_x, max_y)
                valid_plateau = True
                return plateau
            except InvalidPlateauError as err:
                print(str(err))
                print(
                    "Please try entering the plateau dimensions again or type 'abort' "
                    "to abort mission processing.\n"
                )


class Position:
    """
    Represent a position on the rectangular grid on which rovers operate.

    `x` and `y` attributes must be within the minimum and maximum `x` and `y`
    attributes of the mission `Plateau`.

    Attributes:
        x: The x-coordinate of the `Position` on the rectangular mission
            `Plateau`
        y: The y-coordinate of the `Position` on the rectangular mission
            `Plateau`
        direction: a `CompassDirection` enum member representing the cardinal
            direction that the `Position` is facing (NESW).
    """

    def __init__(self, x: int, y: int, direction: CompassDirection) -> None:
        """
        Initialise the position attributes.

        Args:
            x: The x-coordinate the position represents.
            y: The y-coordinate the position represents.
            direction: The direction of facing the position represents.

        Raises:
            InvalidPositionError: When `x` or `y` values are invalid.
            TypeError: When a type other than `CompassDirection` is passed as
                an argument to `direction`.
        """
        self.x = x
        self.y = y
        self.direction = direction

    @property
    def x(self) -> int:
        """
        Returns the position's `x` coordinate.
        """
        return self._x

    @x.setter
    @argument_type_validator({"value": int})
    def x(self, value: int) -> None:
        """
        Sets the position's `x` coordinate.

        Raises:
            InvalidPositionError: When a negative value is passed.
        """
        if value < 0:
            raise InvalidPositionError(f"The x value cannot be negative. Got {value}")

        self._x = value

    @property
    def y(self) -> int:
        """Returns the position's `y` value as an integer."""
        return self._y

    @y.setter
    @argument_type_validator({"value": int})
    def y(self, value: int) -> None:
        """
        Sets the position's `y` value as an integer.

        Raises:
            InvalidPositionError: if a negative value is passed.
        """
        if value < 0:
            raise InvalidPositionError(f"The y value cannot be negative. Got {value}")

        self._y = value

    @property
    def direction(self) -> CompassDirection:
        """
        Returns the position's `direction`.
        """
        return self._direction

    @direction.setter
    @argument_type_validator({"value": CompassDirection})
    def direction(self, value: CompassDirection) -> None:
        """
        Sets the position's `direction`.
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

    def to_dict(self) -> dict[str, Any]:
        """
        Return the class attributes as a dictionary.

        Args:

        Examples:
            ```python
            >>> position = Position(1, 2, N)
            >>> position.to_dict()
            {'x': 1, 'y': 2, 'direction': 'N'}
            ```
        """

        return {"x": self.x, "y": self.y, "direction": self.direction.value}

    @classmethod
    @argument_type_validator({"parameters": dict})
    def from_dict(cls, parameters: dict[str, Any]) -> "Position":
        """
        Construct a `Position` instance from a dictionary.

        Args:
            parameters: A dictionary containing the required parameters
                to instantiate a `Position` object. The required keys
                are `x`, `y` and `direction`. `x` and `y` must be
                non-negative integers. `direction` must be a single
                character string representing a direction of facing
                where `'N'` = `NORTH`, `'E'` = `EAST`, `'S'` = `SOUTH` and
                `'W'` = `WEST`.

        Returns:
            An instance of `Position` with `x`, `y` and `direction`
                attributes mapped to the dictionary passed to `parameters`.

        Raises:
            LoadFromDictError: When the `dict` passed to `parameters` does
                not contain all of the required keys.

        Examples:
            >>> position_dict = {'x': 1, 'y': 2, 'direction': 'N'}
            >>> position = Position.from_dict(position_dict)
            >>> position.x
            1
            >>> position.y
            2
            >>> position.direction
            CompassDirection.NORTH
        """
        reqd_keys = ["x", "y", "direction"]
        for reqd_key in reqd_keys:
            if reqd_key not in parameters:
                err_msg = (
                    f"The parameters dictionary passed to Position.from_dict() "
                    f"is missing the {reqd_key} parameter"
                )
                logger.error(err_msg)
                raise LoadFromDictError(err_msg)

        return cls(
            parameters["x"], parameters["y"], CompassDirection(parameters["direction"])
        )

    @classmethod
    def from_input(cls, plateau: Plateau | None = None) -> "Position | None":
        """
        Construct a `Position` instance from user prompting.

        If the user enters an invalid response an error message is printed and the user
        is prompted again for input.

        `'abort'` can be entered as a user response which will cause this function to
        return `None` which allows the `mission_cli` to abort mission loading.

        Returns:
            An instance of `Position` if user enters valid response. `None` if user
            response is `'abort'`.
        """
        valid_position = False
        while not valid_position:
            user_input = input(
                f"\nEnter the starting position of the rover. This must be in the "
                f"format {ORANGE_BOLD}'1 2 N'{RESET} where:\n"
                f" - {ORANGE_BOLD}1{RESET} is the x coordinate\n"
                f" - {ORANGE_BOLD}2{RESET} is the y coordinate\n"
                f" - {ORANGE_BOLD}N{RESET} is the compass direction the rover is facing (NESW)\n\n"
                f"{BLUE_BOLD}Enter rover position here: {RESET}"
            )
            if user_input == "abort":
                print("Aborting mission loading...")
                return None
            try:
                starting_position = parse_position(user_input)
                x, y, direction = (
                    starting_position["x"],
                    starting_position["y"],
                    CompassDirection(starting_position["direction"]),
                )
                if plateau is not None and (x > plateau.max_x or y > plateau.max_y):
                    raise InvalidPositionError(
                        f"Position is not within the bounds of the specified "
                        f"plateau.\n"
                        f"Plateau max_x: {plateau.max_x} | Position x: {x}\n"
                        f"Plateau max_y: {plateau.max_y} | Position y: {y}"
                    )
                position = cls(x, y, direction)
                return position
            except InvalidPositionError as err:
                logger.error(str(err))
                print(str(err))
                print(
                    "\nPlease try entering the rover's starting position again or type "
                    "'abort' to abort mission processing."
                )


class Rover:
    """
    Represent a rover that can be operated within the plateau dimensions.

    Attributes:
        start_position: The rover's position _prior_ to any mission execution.
        instructions: The navigational instructions that the rover will is to
            follow during mission execution.
        plateau: An instance of `Plateau` that contains the plateau's
            dimensions for reference when executing rover navigation.
        rover_type: A `RoverType` enum member representing what type of rover
            the `Rover` instance represents. Defaults to `RoverType.SCIENCE`
            if not specified.
        latest_position: The rover's position _after_ any instructions have
            been executed. Defaults to the same as `start_position` if no
            instructions have been executed.

    """

    def __init__(
        self,
        start_position: Position,
        instructions: str | list[Instruction],
        plateau: Plateau,
        rover_type: RoverType = RoverType.SCIENCE,
        latest_position: Position | None = None,
    ) -> None:
        """
        Initialise the rover attributes

        Args:
            start_position: The starting position of the rover _prior_ to execution
                of mission instructions.
            instructions: The navigational instructions the rover is to follow during
                mission execution.
            plateau: The mission `Plateau`.
            rover_type: The type of rover to be represented. Defaults to
                `RoverType.SCIENCE` if not specified.
            latest_position: The rover's position _after_ execution of mission
                instructions. Defaults to the same as `start_position` if no
                instructions have been executed.

        Raises:
            InvalidPositionError: When the starting position contains coordinates
                that are outside of the minimum or maximum `x` or `y` dimensions
                of the mission's plateau.
        """
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

        self.start_position = deepcopy(start_position)
        # self.latest_position should be set to the value of the latest_position argument
        # if one has been provided e.g. by attempting to load a Rover using the
        # Rover.from_dict() class method. Where no latest position is passed as an
        # argument it should default to the start position.
        self.latest_position = (
            deepcopy(latest_position) if latest_position else deepcopy(start_position)
        )
        self.instructions = instructions
        self.rover_type = rover_type
        logger.info(
            f"Successfully initialised rover. start_position: {self.start_position} | "
            f"Rover Type: {self.rover_type} | "
            f"Movement Speed: {self.movement_speed} | "
            f"Instructions: {self.instructions}"
        )

    @property
    def start_position(self) -> Position:
        """Return the start position."""
        return self._start_position

    @start_position.setter
    @argument_type_validator({"position": Position})
    def start_position(self, position: Position) -> None:
        """
        Set the start position.

        Args:
            position: A `Position` instance representing the rover's starting
                position.
        """
        self._start_position = position

    @property
    def instructions(self) -> list[Instruction]:
        """Return the rover's instructions."""
        return self._instructions

    @instructions.setter
    @argument_type_validator({"instructions": (str, list)})
    def instructions(self, instructions: str | list[Instruction]) -> None:
        """
        Set the rover's instructions.

        Args:
            instructions: A string with a sequence of valid characters or
                a list of `Instruction` enum members. If passing a string,
                the valid characters are `'L'` = left rotate, `'R'` = right
                rotate and `'M'` = move.
        """
        if isinstance(instructions, str):
            self._instructions = parse_instructions(instructions)
        else:
            self._instructions = instructions

    @property
    def latest_position(self) -> Position:
        """Return the latest position."""
        return self._latest_position

    @latest_position.setter
    @argument_type_validator({"position": Position})
    def latest_position(self, position: Position) -> None:
        """
        Set the latest position.

        Args:
            position: A `Position` instance representing the rover's latest
                position.
        """
        self._latest_position = position

    @property
    def rover_type(self) -> RoverType:
        """Return the rover type."""
        return self._rover_type

    @rover_type.setter
    @argument_type_validator({"rover_type": RoverType})
    def rover_type(self, rover_type: RoverType) -> None:
        """
        Set the rover type.

        Args:
            rover_type: A member of the `RoverType` enum.
        """
        self._rover_type = rover_type

    @property
    def movement_speed(self) -> int:
        """
        Return the rover's movement speed.

        The movement speed is dependent on `rover_type` and is
        retrieved from the `MOVEMENT_SPEED` lookup dictionary.
        """
        return MOVEMENT_SPEED[self.rover_type]

    @argument_type_validator({"plateau": Plateau})
    def _move(self, plateau: Plateau) -> Position:
        """
        Move the rover in the direction in the direction it is facing.

        The distance moved is determined by `movement_speed`.

        The mission's `Plateau` is passed as an argument so that this
        function can determine when a move would take the rover outside
        of the minimum and maximum dimensions of the `Plateau`. If the
        move would take the rover beyond the bounds of the `Plateau`,
        the move is aborted.

        Args:
            plateau: The mission `Plateau` instance.
        """
        initial_position = repr(self.latest_position)
        logger.info(f"Moving rover at position: {initial_position}")
        start_x = self.latest_position.x
        start_y = self.latest_position.y
        base_x_move = MOVEMENTS[self.latest_position.direction]["x_change"]
        base_y_move = MOVEMENTS[self.latest_position.direction]["y_change"]
        movement_speed_multiplier = self.movement_speed
        new_x = start_x + (base_x_move * movement_speed_multiplier)
        new_y = start_y + (base_y_move * movement_speed_multiplier)

        # Verify whether the move would take the rover outside of the bounds
        # of the mission `Plateau`. Abort the move if the rover would be
        # taken beyond the bounds of the `Plateau`.
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
        """
        Rotate the rover left or right by 90 deg.

        Args:
            instruction: A member of the `Instruction` enum specifying
                whether to rotate left or right.
        """
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
        """
        Navigate the rover according to its instructions.

        Takes the mission's `Plateau` as an argument so that it can be
        referenced to ensure the rover does not move beyond plateau's bounds.

        Updates the `latest_position` attribute of this instance of `Rover` to
        the final rover position once all instructions are executed as well as
        returning it.

        Args:
            plateau: The mission's `Plateau` instance.

        Returns:
            A `Position` instance of the rover's final position once all
                instructions are executed.
        """
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

    def __eq__(self, other) -> bool:
        return (
            self.start_position == other.start_position
            and self.latest_position == other.latest_position
            and self.instructions == other.instructions
            and self.rover_type == other.rover_type
        )

    def instructions_to_string(self) -> str:
        """
        Return a string of characters representing the rover's `instructions`.

        Returns:
            A string of the rover's instructions.

        Examples:
            >>> rover = Rover(
            ...     Position(1, 2 CompassDirection.NORTH),
            ...     'LMR',
            ...     Plateau(5, 5)
            ... )
            >>> rover.instructions_to_string()
            'LMR'
        """
        instructions_to_char = [instruction.value for instruction in self.instructions]
        return "".join(instructions_to_char)

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary containing the rover's attributes.

        Returns:
            A dictionary of the rover's attributes.

        Examples:
            >>> rover = Rover(
            ...     Position(1, 2 CompassDirection.NORTH),
            ...     'LMR',
            ...     Plateau(5, 5)
            ... )
            >>> rover.to_dict()
            {
                'start_position': {'x': 1, 'y': 2, 'direction': 'N'},
                'latest_position':  {'x': 1, 'y': 2, 'direction': 'N'},
                'instructions': 'LMR',
                'rover_type': 'S'
            }
        """
        return {
            "start_position": self.start_position.to_dict(),
            "latest_position": self.latest_position.to_dict(),
            "instructions": self.instructions_to_string(),
            "rover_type": self.rover_type.value,
        }

    @classmethod
    @argument_type_validator({"parameters": dict, "plateau": Plateau})
    def from_dict(cls, parameters: dict[str, Any], plateau: Plateau) -> "Rover":
        """
        Construct a `Rover` instance from a dictionary.

        Args:
            parameters: A dictionary containing the required parameters
                to instantiate a `Rover` object. The required keys
                are `start_position`, `latest_position`, `instructions` and
                `rover_type`. `start_position` and `latest_position` values must
                be dictionaries of positions that can be parsed by the
                `Position.from_dict()` method. `instructions` must be the
                instructions a string of a sequence of characters e.g `'LMR'`.
                `rover_type` must be contain a string with a single character
                representing the rover type e.g. `'S'` or `'C'`.
            plateau: The mission `Plateau`.

        Returns:
            An instance of `Rover` with `start_position`, `latest_position`,
                `instructions`, and `rover_type` attributes mapped to the
                dictionary passed to `parameters`.

        Raises:
            LoadFromDictError: When the `dict` passed to `parameters` does
                not contain all of the required keys.

        Examples:
            >>> rover_dict = {
            ...     'start_position': {'x': 1, 'y': 2, 'direction': 'N'},
            ...     'latest_position': {'x': 1, 'y': 2, 'direction': 'N'},
            ...     'instructions': 'LMR',
            ...     'rover_type': 'S'
            ... }
            >>> rover = Rover.from_dict(rover_dict)
            >>> rover.instructions
            [Instruction.LEFT, Instruction.MOVE, Instruction.RIGHT]
            >>> rover.rover_type
            RoverType.SCIENCE
        """
        reqd_keys = {"start_position", "latest_position", "instructions", "rover_type"}
        for reqd_key in reqd_keys:
            if reqd_key not in parameters:
                err_msg = (
                    f"The parameters dictionary passed to Rover.from_dict() "
                    f"is missing the {reqd_key} parameter"
                )
                logger.error(err_msg)
                raise LoadFromDictError(err_msg)

        return Rover(
            Position.from_dict(parameters["start_position"]),
            parse_instructions(parameters["instructions"]),
            plateau,
            RoverType(parameters["rover_type"]),
            Position.from_dict(parameters["latest_position"]),
        )

    def __repr__(self) -> str:
        return json.dumps(self.to_dict())


class Mission:
    """
    Represent a mission and its associated components.

    Attributes:
        plateau: The mission's rectangular plateau.
        rovers: A list of the rovers that are associated with the mission
        timestamp: Timestamp of when the mission was executed.

    """

    def __init__(
        self,
        plateau: Plateau | None = None,
        rovers: list[Rover] | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        """
        Initialise the mission attributes

        Args:
            plateau: A `Plateau` instance representing the rectangular grid
                that rovers and move around on. Can be omitted and set after
                class construction.
            rovers: A list of the `Rover` instances that can be moved around
                within the mission's plateau. Can be omitted and set after
                class construction.
            timestamp: The timestamp of the mission's execution. Can be omitted
                and set after class construction.

        """
        self.plateau = plateau
        self.rovers = rovers
        self.timestamp = timestamp

    @property
    def plateau(self) -> Plateau | None:
        """Return the mission's `Plateau`."""
        return self._plateau

    @plateau.setter
    @argument_type_validator({"plateau": (Plateau, type(None))})
    def plateau(self, plateau: Plateau | None) -> None:
        """
        Set the mission's `Plateau`.

        Args:
            plateau: A valid `Plateau` instance.
        """
        self._plateau = deepcopy(plateau)

    @property
    def rovers(self) -> list[Rover]:
        """Return the mission's `Rover` list."""
        return self._rovers

    @rovers.setter
    def rovers(self, rovers: list | None) -> None:
        """
        Set the mission's `Rover` list.

        Args:
            rovers: A list of `Rover` instances. Can be `None` in which case
            `rovers` is set to an empty list.
        """
        if not rovers:
            self._rovers = []
        else:
            self._rovers = [deepcopy(rover) for rover in rovers]

    @argument_type_validator({"rover": Rover})
    def add_rover(self, rover: Rover) -> None:
        """
        Add a new `Rover` instance to `rovers`.

        Args:
            rover: A valid `Rover` instance.
        """
        self._rovers.append(rover)

    @property
    def timestamp(self) -> datetime | None:
        """Return the mission's timestamp"""
        return self._timestamp

    @timestamp.setter
    @argument_type_validator({"timestamp": (datetime, type(None))})
    def timestamp(self, timestamp: datetime | None) -> None:
        """
        Set the mission's timestamp.

        Args:
            timestamp: A `datetime` object.
        """
        self._timestamp = timestamp

    def to_dict(self) -> dict[str, Any]:
        """
        Return a dictionary of the mission instance's attributes.

        Returns:
            A dictionary of the rover's attributes.

        Examples:
            >>> plateau = Plateau(5, 5)
            >>> rover = Rover(
            ...     Position(1, 2 CompassDirection.NORTH),
            ...     'LMR',
            ...     Plateau(5, 5)
            ... )
            >>> rovers = [rover]
            >>> timestamp = datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
            >>> mission = Mission(
            ...     plateau=plateau,
            ...     rovers=rovers,
            ...     timestamp=timestamp
            ... )
            >>> mission.to_dict()
            {
                'plateau': {'min_x': 0, 'max_x': 5, 'min_y': 0, 'max_y': 5},
                'rovers': [
                    {
                        'start_position': {'x': 1, 'y': 2, 'direction': 'N'},
                        'latest_position': {'x': 1, 'y': 2, 'direction': 'N'},
                        'instructions': 'LMR',
                        'rover_type': 'S'
                    }
                ],
                'timestamp': '2026-01-01T12:00:00+00:00'
            }
        """
        plateau = self.plateau.to_dict() if self.plateau else None
        rovers = [rover.to_dict() for rover in self.rovers]
        timestamp = self.timestamp.isoformat() if self.timestamp else None

        return {"plateau": plateau, "rovers": rovers, "timestamp": timestamp}

    @classmethod
    @argument_type_validator({"parameters": dict})
    def from_dict(cls, parameters: dict) -> "Mission":
        """
            Construct a `Mission` instance from a dictionary.

            Args:
                parameters: A dictionary containing the required parameters
                    to instantiate a `Mission` object. The required keys
                    are `plateau`, `rovers` and `timestamp`. The `plateau` value
                    must be a dictionary of a plateau that can be parsed by the
                    `Plateau.from_dict()` method. The `rovers` value must be a list
                    containing a dictionary for each rover and each dictionary
                    must be able to be parsed by the `Rover.from_dict()` method.
                    The `timestamp` key must be a string in isoformat.

            Returns:
                An instance of `Mission` with `plateau`, `rovers`,
                    and `rover_type` attributes mapped to the dictionary passed to
                    `parameters`.

            Raises:
                LoadFromDictError: When the `dict` passed to `parameters` does
                    not contain all of the required keys.

            Examples:
                >>> mission_dict = {
                ...     'plateau': {'min_x': 0, 'max_x': 8, 'min_y': 0, 'max_y': 8},
                ...     'rovers': [
                ...         {
                ...             'start_position': {'x': 1, 'y': 2, 'direction': 'N'},
                ...             'latest_position': {'x': 1, 'y': 2, 'direction': 'N'},
                ...             'instructions': 'LMR',
                ...             'rover_type': 'S',
                ...         },
                ...     ],
                ...     'timestamp': '2026-01-01T12:00:00+00:00',
        }
                >>> mission = Mission.from_dict(mission_dict)
                >>> mission.timestamp
                2026-01-01 12:00:00+00:00
        """
        reqd_keys = {"plateau", "rovers", "timestamp"}
        for reqd_key in reqd_keys:
            if reqd_key not in parameters:
                err_msg = (
                    f"The parameters dictionary passed to Mission.from_dict() "
                    f"is missing the {reqd_key} parameter"
                )
                logger.error(err_msg)
                raise LoadFromDictError(err_msg)

        plateau = Plateau.from_dict(parameters["plateau"])
        rovers = [Rover.from_dict(rover, plateau) for rover in parameters["rovers"]]
        timestamp = datetime.fromisoformat(parameters["timestamp"])
        return Mission(plateau, rovers, timestamp)

    def __repr__(self) -> str:
        return json.dumps(self.to_dict())

    def __eq__(self, other) -> bool:
        return (
            self.plateau == other.plateau
            and self.rovers == other.rovers
            and self.timestamp == other.timestamp
        )

    @argument_type_validator({"target_directory": (str, Path)})
    def archive(self, target_directory: str | Path) -> Path:
        """
        Write the mission data to disk.

        The data is saved to a JSON file at the target directory with the
        mission timestamp in the filename.

        Args:
            target_directory: Path for where the archive will be written to.

        Returns:
            The path to the saved JSON file.
        """
        directory = (
            Path(target_directory)
            if isinstance(target_directory, str)
            else target_directory
        )

        timestamp = self.timestamp if self.timestamp else datetime.now(timezone.utc)
        timestamp_str = timestamp.strftime("%Y-%m-%d %H_%M_%S")

        file_name = f"mission_archive_{timestamp_str}.json"

        target_path = directory / file_name

        archive_start_msg = f"\nWriting archive to {target_directory} | Filename: {BOLD}{file_name}{RESET}"
        logger.info(archive_start_msg)
        print(archive_start_msg)
        with open(target_path, "w") as file:
            file.write(json.dumps(self.to_dict(), indent=4))

        archive_success_msg = (
            f"\nArchive written successfully to {target_directory} | "
            f"Filename: {BOLD}{file_name}{RESET}\n"
        )
        logger.info(archive_success_msg)
        print(archive_success_msg)

        return target_path

    @classmethod
    def load_from_archive(cls, path: str | Path) -> "Mission | None":
        """
        Construct an instance of the `Mission` class from a saved archive.

        Args:
            path: The location of the mission archive JSON file to be loaded

        Returns:
            A `Mission` class instance

        Raises:
            FileNotFoundError: When the path passed to `path` cannot be found.
        """
        try:
            with open(path, "r") as file:
                loaded_data = json.load(file)

            return cls.from_dict(loaded_data)

        except FileNotFoundError as err:
            err_msg = f"File {path} could not be found: {err}"
            logger.error(err_msg)
            print(err_msg)

    def execute(self, archive_path: str | Path = Path("mission_archive")) -> str:
        """
        Execute a mission.

        Each rover's instructions are executed in turn and the mission is
        written to an archive JSON file.

        Args:
            path: The path where the mission archive JSON file is to be saved.

        Returns:
            A string containing the final positions of each rover which conforms
                to the project's required mission output.

        Examples:
            >>> mission = Mission(...)
            >>> mission.execute()
            1 3 N S
            5 1 E C
        """
        # Validate archive_path exists at the start so that further
        # execution can be stopped before trying to write to a
        # non-existent path
        if not os.path.exists(archive_path):
            err_msg = (
                f"The specified path {archive_path} could not be "
                f"found. Please choose a valid filepath and retry "
                f"execution."
            )
            logger.error(err_msg)
            raise FileNotFoundError(err_msg)

        execute_begin_msg = "\nBeginning mission execution..."
        logger.info(execute_begin_msg)
        print(f"{ORANGE_BOLD}{execute_begin_msg}{RESET}")

        consolidated_output = []
        for rover in self.rovers:
            rover.execute_instructions(self.plateau)

            # This function is require to return the final position of each
            # rover as a string in the below format:
            # 1 3 N S
            # 5 1 E C
            rover_final_pos_str = " ".join(
                [
                    str(rover.latest_position.x),
                    str(rover.latest_position.y),
                    str(rover.latest_position.direction.value),
                    str(rover.rover_type.value),
                ]
            )
            consolidated_output.append(rover_final_pos_str)

        execute_success_msg = "\nMission executed successfully..."
        logger.info(execute_success_msg)
        print(f"{GREEN_BOLD}{execute_success_msg}{RESET}")

        # Executed missions are required to be written to disk.
        self.archive(archive_path)

        return "\n".join(consolidated_output)
