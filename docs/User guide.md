# User Guide
## Install necessary dependencies using command
```bash
poetry install 
```

## Command line functions and Usage
```bash
poetry run dungeon --help
poetry run dungeon --generate            # create PNG (non-interactive)
poetry run dungeon --generate --rooms 50 # exactly 50 rooms
poetry run dungeon --generate --seed 42  # reproducible

poetry run dungeon --game                # open Pygame viewer
poetry run dungeon --game --rooms 30     # viewer with fixed room count
```

## Run tests with command
```bash
poetry run pytest -v
```

## Run coverage report with command
```bash
poetry run coverage report -m
```

## Run Pylint with command
```bash
poetry run pylint src/dungeon_generator
```

## Overall generation

- A tiled dungeon composed of rectangular rooms connected by corridors.

- Optionally a Delaunay triangulation and MST under the hood to ensure overall connectivity.

- The dungeon can be exported to PNG or explored in the viewer.

## Room count and randomness

- You can request a room count with --rooms N. The algorithm tries to place all rooms, but high values in a small map can’t always be satisfied due to space and non-overlap rules.

- --rooms to let the program pick a reasonable range (approx. 3–100).

- Add --seed S to make results repeatable.

## Viewer controls (Pygame)

- R – regenerate a fresh layout (uses --rooms if provided).

- Esc – quit the viewer (or close the window).

## Example workflows
```bash
poetry run dungeon --game --rooms 30
```