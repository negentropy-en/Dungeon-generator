# Testing Document

## Test coverage

![Poetry Coverage](./docs/screenshots/coverage-report.png)

## Testing

What has been tested and how:

- Point Class - Basic 2D point functionality
Creation, equality, hashing, string representation
Used coordinate comparisons and set operations

- Triangle and Delaunay Triangulation - Geometric algorithms
Circumcircle calculations for different triangle types
Delaunay property validation
Bowyer-Watson algorithm implementation
Bresenham-style line utility is exercised

- Room and Dungeon Generation - Core dungeon logic
Room placement, intersection detection, bound checking
MST connectivity using Kruskal's algorithm
Grid generation and corridor creation

- A* Pathfinding - Navigation system
Pathfinding in open spaces, around obstacles, no-path scenarios
8-directional movement with proper cost calculation

- Integration tests - System functionality
Full dungeon generation to pathfinding pipeline
Seed-based reproducibility
Cross-room connectivity validation

## Test inputs used
- Geometric: Points, triangles, rooms with various coordinates and sizes
- Grids: Open spaces, wall mazes, completely blocked areas
- Parameters: Different dungeon sizes, room counts
- Edge cases: Tiny dungeons, large rooms in small spaces
- Random seeds: 42, 123, 999 for reproducible testing

## How to repeat tests
```bash
poetry run pytest -v    # To run all the tests
```

```bash
poetry run pytest --cov=dungeon_generator --cov-report=term-missing # To include coverage
```