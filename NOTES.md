# Project Notes

## Logic Layer

The logic layer processes mission data as formatted by the input layer and consisting of:

- Mission Plateau size
- Rover Data:
    - Starting Postion
    - Instructions

The data is formatted like this:

```python
{
    "plateau": {"max_x": 5, "max_y": 5},
    "rovers": [
        {
            "position": {"x": 1, "y": 2, "direction": "N"},
            "instructions": ["L", "M", "L", "M", "L", "M", "L", "M", "M"],
        },
        {
            "position": {"x": 3, "y": 3, "direction": "E"},
            "instructions": ["M", "M", "R", "M", "M", "R", "M", "R", "R", "M"],
        },
    ],
}
```

### Processing Movement Instructions

To process instructions, a lookup table will be created as a constant to help determine:
- What direction a rover faces once it has been rotated by and `L` or `R` instruction
- How to modify the rover's position when it moves due to an `M` instruction

The change to the rover's position is dependent on the direction it is facing:

|Rover's Direction|Change When Moved in this direction|
|---|---|
|North|`y + 1`|
|East|`x + 1`|
|South|`y - 1`|
|West|`x - 1`|

### Orchestration of Mission Processing

`main.py` will handle the orchestration of the mission processing logic by accepting a mission text with starting positions and processing each rover in turn as shown in the below diagram:

![alt text](image.png)

### `execute_instructions()` Exception Handling

The below custom exceptions have been created to help with orchestrating mission processing:

`InvalidInstructionError`: Raised when a malformed instructions string is passed to the `parse_instructions()` function.

`InvalidPlateauError`: Raised when a malformed plateau dimensions string is passed to the `parse_plateau()` function.

`InvalidPositionError`: Raised when a malformed position string is passed to the `parse_position()` function.

The above cover the most likely errors that are likely to occur when a mission is processed.

All of the above inherit from the `MissionError` exception which inherits from `Exception`.

> NOTE:- If any of the above exceptions is raised during the mission processing function (`execute_mission()`) the function will abort processing the mission and print an error message to the terminal.

## Refactoring into Classes

The project is required to refactor the existing functions into classes. The required classes are:
- `Plateau`
- `Rover`
- `Position`

Three question are required to be answered:

1. What state belongs in each class?
- The `Plateau` class will hold the maximum dimensions of the mission plateau grid. On construction it will validate that the supplied max dimensions are valid.
- The `Rover` class will hold a rover's starting position and its mission instructions. The starting position will be an instance of the `Position` class. A second instance of the `Position` class will hold the rover's final position once its instructions have been executed.
- The `Position` class will hold `x`, `y` and `direction` attributes which represent a rover's position on the map and in which direction it is facing.

2. What methods does each class have?
```python
class Plateau:
    def __init__(self, max_x: int, max_y: int) -> None: ...

    @property
    def min_x(self) -> int: ...

    @property
    def max_x(self) -> int: ...

    @max_x.setter
    def max_x(self, value: int) -> None: ...

    @property
    def max_y(self) -> int: ...

    @max_y.setter
    def max_y(self, value: int) -> int: ...

    def __repr__(self): ...


class Rover:
    def __init__(self, start_position: Position, mission: str): ...

    @property
    def start_position(self) -> Position: ...

    @start_position.setter
    def start_position(self, x: int, y: int, direction: CompassDirection) -> None: ...

    @property
    def instructions(self) -> list[Instruction]: ...

    @instructions.setter
    def instructions(self, instructions: str | list[Instruction]) -> None: ...

    @property
    def latest_position(self) -> Position: ...

    @new_position.setter
    def latest_position(self, x: int, y: int, direction: CompassDirection) -> None: ...

    def _move(starting_position: Position) -> Position: ...

    def _rotate(starting_position: Position, direction: Instruction) -> Position: ...

    def execute_instructions(
        self, start_position: Position, instructions: List[Instruction]
    ) -> Position: ...


class Position:
    def __init__(self, x: int, y: int, direction: CompassDirection) -> None: ...

    @property
    def x(self) -> int: ...

    @x.setter
    def x(self, value: int) -> None: ...

    @property
    def y(self) -> int: ...

    @y.setter
    def y(self, value: int) -> None: ...

    @property
    def direction(self) -> CompassDirection: ...

    @direction.setter
    def direction(self, value: CompassDirection) -> None: ...

    def __eq__(self): ...

    def __repr__(self): ...
```

## Validation

Each class' `@setter` methods are decorated by the `argument_type_validation` decorator to ensure that invalid data types are identified and meaningful exceptions are raised in response.

Other validation:

- `Plateau()`
    - `max_x` and `max_y` attributes are validated by their `@setter` methods to ensure both values are greater than 0.
- `Position()`
    - `x` and `y` values are validated by their `@setter` methods to ensure that neither value is negative.
- `Rover()`
    - `start_position` is validated in the `__init__` method to ensure that the rover's starting position is within the bounds of the mission `Plateau()`.
    - The `_move()` method validates whether the move it is trying to execute would take the rover outside of the bounds of the mission `Plateau()` and maintains the rover's `latest_position` as unchanged if the move would take the rover outside of the `Plateau()` bounds.

## Adding a Second Rover Class

The project brief requires the ability to cater for a second "cargo" rover which moves two places forward with each move rather than the base value of one place forward per move.

I will implement this by adding two new attributes to the `Rover()` class called `rover_type` and `movement_speed`. `rover_class` will be an `enum` which holds the value of which type any given instance of the `Rover()` class represents. The `movement_speed` attribute will represent how many places the rover moves with each invokation of the `_move()` method. I will make the value of `movement_speed` a lookup based on the `rover_type` attribute. The value of this will be 1 for the existing ("science") rover and 2 for the new "cargo" rover.

To accomodate this when parsing and executing a mission, the format of the mission input must change so that it contains a value specifying each rover's type. To achieve this, the format of lines within the mission text that define a rover's position will change to include an additional single letter

The rationale for using this approach is to minimise the amount of new and changed code required to implement the additional rover since the new rover is identical to the existing once except for movement speed. Implementing a `rover_type` and associated speed lookup should facilitate simpler addition of further rovers at a later point.

To further minimise disruption caused by the change, the "science" rover will be treated as the default rover so that the `rover_type` argument can be omitted when instantiated a `Rover()` class. Additionally, `movement_speed` will be handled as a multiplier when applying it to the `_move` method. This should make it unnecessary to modify the `MOVEMENTS` lookup dictionary and the mechanism by which it is referenced in order to execute the `_move()` command. This should mean that existing tests that are predicated around a rover moving a single space per move should still pass after the implementation of the `movement_speed` attribute. It should only be necessary to write a new test to assert that the movement speed attribute does cause the "cargo" rover to move at two spaces per invokation of the `_move()` method as expected.
