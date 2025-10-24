# Specification Document

This specification document defines the assignment to be completed in the University of Helsinki's Subject Studies Assignment: Algorithms and AI Project.

I am taking this course in the Bachelor's in Computer Science (TKT) program.

## Subject and implementation

The project generates connected, reproducible dungeon maps made of non-overlapping rectangular rooms and orthogonal corridors. Generation runs as a simple pipeline: rooms are sampled and placed inside an inner margin with one-tile padding from the outer border, ensuring they never touch the edge; room centers are triangulated with Bowyer–Watson; a minimum spanning tree (Kruskal) selects the corridors that guarantee connectivity; L-shaped grid routes are laid between connected rooms; finally, rooms and corridors are rasterized onto a grid used for rendering and pathfinding.

The command-line interface has two modes. “Generate” builds a dungeon and writes a PNG image; “game” opens a small Pygame viewer where you can regenerate with R and quit with Esc. Both modes accept --rooms and --seed. The data model is intentionally minimal: rooms with positions and centers, triangles for connectivity, corridor polylines as grid coordinates, and a 2D integer grid where 1 = floor and 0 = wall.

Performance is practical for up to ~100 rooms: room placement is quadratic in the worst case, triangulation is near n log ⁡n in practice, Kruskal is n log n, and rasterization is linear in room area plus corridor length. Correctness is enforced with invariants (in-bounds, non-overlap, connectivity) and automated tests, including failure paths and an A* smoke test. Linting keeps the code tidy.

## Programming languages

This project will be done in Python. 
Peer review can be done in Python, Java, or C. 

## Project language

Project language is English. Code, variable names as well as other comments will also be in English. 

## Sources

For this project, I'm using the following as source material:

- [Delaunay triangulation (Wikipedia)](https://en.wikipedia.org/wiki/Delaunay_triangulation)
- [Kruskal’s algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Kruskal%27s_algorithm)
- [A* search algorithm (Wikipedia)](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [Bowyer-Watson algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Bowyer%E2%80%93Watson_algorithm)
- [Bresenham's line algorithm (Wikipedia)](https://en.wikipedia.org/wiki/Bresenham%27s_line_algorithm)