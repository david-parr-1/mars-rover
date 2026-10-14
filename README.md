# Orion 7 Mars Rover Mission

A Python command-line application for planning and executing rover missions on a rectangular Mars plateau. Enter a plateau and one or more rovers interactively; the application runs each rover's instructions in order and saves the outcome as a JSON archive.

## Features

- Interactive prompts for plateau dimensions and rover details
- Science rovers, which move one grid square for each `M` instruction
- Cargo rovers, which move two grid squares for each `M` instruction
- Left and right 90-degree turns, with movement kept within the plateau
- Input validation with clear errors and the option to abort mission entry
- Timestamped JSON archives containing the plateau and rover mission data
- Unit and integration tests

## Requirements

- Python 3.10 or later
- `pip`

## Set up

From the project root, create and activate a virtual environment, then install the project dependencies:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run a mission

Start the interactive application from the project root:

```bash
python main.py
```

Follow the prompts to:

1. Enter the plateau's maximum `x` and `y` coordinates, separated by a space (for example, `5 5`). The lower-left coordinate is always `(0, 0)`.
2. Select a rover type: `S` for Science or `C` for Cargo.
3. Enter the rover's starting position as `x y direction` (for example, `1 2 N`).
4. Enter its instruction string, then choose whether to add another rover.

Starting positions must be on the plateau, including its edges. Coordinates and plateau dimensions are non-negative and positive respectively; the plateau dimensions are limited to two digits (`1`-`99`). Enter `abort` at a prompt to cancel mission entry.

### Instructions and movement

Instructions are entered as one continuous string, using only:

| Instruction | Action |
| --- | --- |
| `L` | Turn left by 90 degrees without moving |
| `R` | Turn right by 90 degrees without moving |
| `M` | Move forward in the direction the rover is facing |

The compass directions are `N` (north), `E` (east), `S` (south), and `W` (west). North increases `y`; east increases `x`. A move that would place the rover outside the plateau is ignored. Rovers execute their instructions sequentially, one rover at a time.

For example, a Science rover starting at `1 2 N` with instructions `LMLMLMLMM` finishes at `1 3 N`. A Cargo rover takes two-square steps for `M`; if the full two-square move would leave the plateau, the rover stays where it is for that instruction.

### Results and archives

The application displays each rover's final position as `x y direction type`, one rover per line. The type is `S` or `C`; for example:

```text
1 3 N S
5 1 E S
```

Each completed mission is saved as a timestamped JSON file in the existing `mission_archive/` directory. The archive records the plateau, each rover's starting and final positions, rover type, instructions, and mission timestamp. The application prints the archive filename when it is saved.

## Run the tests

With the virtual environment activated, run the test suite from the project root:

```bash
pytest
```

To run the linter:

```bash
ruff check .
```

## Project layout

```text
.
├── main.py                 # Mission execution and interactive command-line interface
├── src/
│   ├── classes.py          # Plateau, Position, Rover, and Mission models
│   ├── custom_enums.py     # Instruction, CompassDirection and RoverType enums
│   ├── input_layer.py      # Mission parsing and input validation
│   ├── logic_layer.py      # Rover movement and rotation logic
│   ├── exceptions.py       # Mission-specific exceptions
│   ├── logging_config.py   # Application logging setup
│   └── text_colours.py     # Constants for colours used in terminal text
├── tests/                  # Unit and integration tests
├── mission_archive/        # Generated mission JSON archives
├── requirements.txt        # Python package dependencies
└── NOTES.md                # Project design notes
```
