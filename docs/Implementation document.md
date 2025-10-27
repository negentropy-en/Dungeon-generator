# Implementation Document
## Overall structure
- The program is organized into several different modules that work together to generate procedural dungeons.

## Core Modules
- Dungeon.py - Main dungeon generation logic, room placement, and MST construction
- Delaunay.py - Delaunay triangulation implementation using Bowyer-Watson algorithm
- Pathfinding.py - A* pathfinding for navigation and connectivity validation
- Visualization.py - Matplotlib-based 2D visualization and PNG export
- Game_interface.py - Pygame-based interactive dungeon explorer
- Main.py - CLI and program entry point
- Test_dungeon.py - Includes all unit tests for the application.

## Data Flow
- Room generation -> Creates non-overlapping rectangular rooms
- Delaunay triangulation -> Connects room centers with triangles
- Minimum Spanning Tree -> Creates efficient corridor connections
- Grid Generation -> Converts rooms and corridors to 2D walkable grid
- Visualization/Game -> Presents results to user

## Time and Space complexity
- Delaunay Triangulation: Time complexity is 0(n^2) in worst case, 0(n log n) in practice. Space complexity is 0(n) for storing triangles and points.
- Kruskal's algorithm (MST): Time complexity is 0(n log n). Space complexity is 0(n).
- A* pathfinding: Time complexity is 0(V log V) for worst case where V = number of walkable cells, 0(V log V + E) in practice over explored region where E = explored edges. Space complexity is 0(V) for open/closed sets and path reconstruction.
- Room placement/generation: Time complexity is 0(n^2) in worst case. Space complexity is 0(n).

## Problems
- Fixed sizes and grid; reduces the probability for very high requested room counts.
- Triangulation depends on floating-point circumcircle tests.
- Limited room types and corridors; corridors are based L-shaped connections and room types are rectangular shapes.
- Testing is only done on key components; Core algorithms (Delaunay triangulation, MST, A* pathfinding), data structures (point, triangle, room, node), basic dungeon generation pipeline, and other geometric/mathematical operations. 

## Possible improvements
- Algorithm enhancements; more sophisticated corridor generation, binary space partition for room layouts etc..
- Variable room shapes
- Comprehensive testing for all parts; visualization, game interface, error handling, performance testing, and user interface testing.

## Use of Large Language Models (LLMs)
- In this project LLMs (OpenAI ChatGPT 5 model) were used to narrow down the subject from the original aspect, describe possible error messages/handling/debugging, fetched guidelines how to utilize pylint and poetry as well as documentation structure.

## Sources

For this project, I'm using the following as source material:

- [Delaunay triangulation (Wikipedia)](https://en.wikipedia.org/wiki/Delaunay_triangulation)
- [Kruskal’s algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [A* search algorithm (Wikipedia)](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Bowyer-Watson algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Bowyer%E2%80%93Watson_algorithm)
- [Bresenham's line algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm)
- [Procedurally Generated Dungeons (Vazgriz)](https://vazgriz.com/119/procedurally-generated-dungeons/)
- [List of interesting dungeon generators (GitHub)](https://github.com/bluetyson/random-dungeon-generators)