# Dungeon-generator
Algorithms and AI Project

A Python implementation of a procedural dungeon generator using Delaunay triangulation and Minimum Spanning Trees for connectivity.

## Features
- Image creation: save a PNG of the generated dungeon with Matplotlib.
- Interactive viewer (Pygame): regenerate and explore dungeons in a simple window.
- Deterministic seeds: Reproduce layouts with --seed.
- Command-line interface: Choose generation mode and room count.

## Documentation
- [Specification Document](docs/Specification_document.md)
- [Implementation Document](docs/Implementation_document.md)
- [Testing Document](docs/Testing_document.md)
- [User Guide](docs/User_guide.md)
- [Weekly Reports](docs/weekly_reports/)

## Installation
This project is managed with [Poetry](https://python-poetry.org/).

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