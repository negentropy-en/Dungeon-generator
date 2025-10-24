import random
import math
import logging
from .delaunay import Point, DelaunayTriangulation

# Set up logging
logger = logging.getLogger(__name__)


class Room:  # Room class representing a rectangular room in the dungeon
    def __init__(self, x, y, width, height, room_id):
        # Initializing the room with position, size, and ID
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = Point(x + width / 2, y + height / 2)
        self.id = room_id
        self.connections = []
        self.doors = []

    def intersects(self, other):  # Checking if the room intersects with another room
        return (
            self.x <= other.x + other.width
            and self.x + self.width >= other.x
            and self.y <= other.y + other.height
            and self.y + self.height >= other.y
        )

    def contains_point(self, x, y):  # Checking if a point is inside the room
        return self.x <= x <= self.x + self.width and self.y <= y <= self.y + self.height

    def __repr__(self):
        return f"Room({self.id}: {self.x}, {self.y}, {self.width}, {self.height})"


class Door:  # Door class representing a door connecting two rooms
    def __init__(self, x, y, room1, room2):
        self.x = x
        self.y = y
        self.room1 = room1
        self.room2 = room2

    def __repr__(self):
        return f"Door({self.x}, {self.y})"


class DungeonGenerator:  # Main dungeon generator class
    def __init__(
        self,
        width=100,
        height=100,
        max_rooms=15,
        min_room_size=5,
        max_room_size=15,
    ):
        if width < 10 or height < 10:
            raise ValueError("Dungeon dimensions must be at least 10x10")
        if max_rooms < 1:
            raise ValueError("Must generate at least 3 rooms")
        if min_room_size < 3 or max_room_size < min_room_size:
            raise ValueError("Invalid room size parameters")

        self.width = width
        self.height = height
        self.max_rooms = max_rooms
        self.min_room_size = min_room_size
        self.max_room_size = max_room_size
        self.rooms = []
        self.corridors = []
        self.doors = []
        self.triangulation = None
        self.grid = None

    def generate_rooms(self):  # Generate non-overlapping rooms
        attempts = self.max_rooms * 5
        generated = 0

        for _ in range(attempts):
            if len(self.rooms) >= self.max_rooms:
                break

            room_width = random.randint(self.min_room_size, self.max_room_size)
            room_height = random.randint(self.min_room_size, self.max_room_size)

            # Ensure room fits within bounds
            if room_width >= self.width - 2 or room_height >= self.height - 2:
                continue

            room_x = random.randint(1, self.width - room_width - 1)
            room_y = random.randint(1, self.height - room_height - 1)
            new_room = Room(room_x, room_y, room_width, room_height, len(self.rooms))

            if any(new_room.intersects(other_room) for other_room in self.rooms):
                continue

            self.rooms.append(new_room)
            generated += 1

        logger.info("Generated %d rooms after %d attempts", generated, attempts)
        return generated

    def generate_delaunay(self):  # Generate Delaunay triangulation of room centers
        if len(self.rooms) < 3:
            logger.warning("Need at least 3 rooms for Delaunay triangulation")
            self.triangulation = None
            return False

        try:
            points = [room.center for room in self.rooms]
            self.triangulation = DelaunayTriangulation(points)
            logger.info(
                "Created Delaunay triangulation with %d triangles",
                len(self.triangulation.triangles),
            )
            return True
        except Exception as e:
            logger.error("Failed to create Delaunay triangulation: %s", e)
            self.triangulation = None
            return False

    def generate_mst(self):  # Generate MST from Delaunay triangulation
        if not self.triangulation:
            self.generate_delaunay()
        if not self.triangulation:
            logger.error("Cannot generate MST without triangulation")
            return False

        all_edges = set()

        # Extract edges from Delaunay triangulation
        for triangle in self.triangulation.triangles:
            room_map = {r.center: r for r in self.rooms}

            p1, p2, p3 = triangle.vertices
            r1, r2, r3 = room_map.get(p1), room_map.get(p2), room_map.get(p3)

            # Add edges with distance
            if r1 and r2:
                dist = math.hypot(r1.center.x - r2.center.x, r1.center.y - r2.center.y)
                edge_key = (min(r1.id, r2.id), max(r1.id, r2.id), dist)
                all_edges.add(edge_key)
            if r2 and r3:
                dist = math.hypot(r2.center.x - r3.center.x, r2.center.y - r3.center.y)
                edge_key = (min(r2.id, r3.id), max(r2.id, r3.id), dist)
                all_edges.add(edge_key)
            if r3 and r1:
                dist = math.hypot(r3.center.x - r1.center.x, r3.center.y - r1.center.y)
                edge_key = (min(r3.id, r1.id), max(r3.id, r1.id), dist)
                all_edges.add(edge_key)

        if not all_edges:
            logger.error("No edges found in triangulation")
            return False

        sorted_edges = sorted(list(all_edges), key=lambda item: item[2])

        # Kruskal's algorithm for MST with Union-Find
        parent = list(range(len(self.rooms)))

        def find(i):  # Find root of node i with path compression
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):  # Union two sets containing i and j; by root
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_j] = root_i
                return True
            return False

        mst_edges = []
        for u, v, _ in sorted_edges:
            if union(u, v):
                mst_edges.append((self.rooms[u], self.rooms[v]))

        # Add extra edges for loops (20% of MST edges)
        extra_edge_ratio = 0.2
        num_extra_edges = int(len(mst_edges) * extra_edge_ratio)
        potential_extra_edges = [
            (self.rooms[u], self.rooms[v])
            for u, v, _ in sorted_edges
            if (self.rooms[u], self.rooms[v]) not in mst_edges
            and (self.rooms[v], self.rooms[u]) not in mst_edges
        ]
        random.shuffle(potential_extra_edges)

        final_edges = mst_edges + potential_extra_edges[:num_extra_edges]

        # Create corridors and mark connections
        for room1, room2 in final_edges:
            room1.connections.append(room2.id)
            room2.connections.append(room1.id)
            self.create_corridor_between_rooms(room1, room2)

        logger.info(
            "Created MST with %d base edges and %d total edges",
            len(mst_edges),
            len(final_edges),
        )
        return True

    def create_corridor_between_rooms(self, room1, room2):  # L-shaped corridor
        x1, y1 = int(room1.center.x), int(room1.center.y)
        x2, y2 = int(room2.center.x), int(room2.center.y)

        path = []
        if random.choice([True, False]):  # Horizontal then vertical
            path.append((x1, y1))
            path.append((x2, y1))
            path.append((x2, y2))
        else:  # Vertical then horizontal
            path.append((x1, y1))
            path.append((x1, y2))
            path.append((x2, y2))

        self.corridors.append(path)

    def generate_grid(self):  # Generating 2D grid representation
        try:
            self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]

            # Mark room cells, value 1 = walkable
            for room in self.rooms:
                for y in range(room.y, room.y + room.height):
                    for x in range(room.x, room.x + room.width):
                        if 0 <= y < self.height and 0 <= x < self.width:
                            self.grid[y][x] = 1

            # Mark corridor cells, value 1 = walkable
            for corridor in self.corridors:
                for i in range(len(corridor) - 1):
                    x1, y1 = corridor[i]
                    x2, y2 = corridor[i + 1]
                    for x, y in self.get_line_points(int(x1), int(y1), int(x2), int(y2)):
                        if 0 <= y < self.height and 0 <= x < self.width:
                            self.grid[y][x] = 1

            logger.info("Generated %dx%d grid", self.width, self.height)
            return True

        except Exception as e:
            logger.error("Failed to generate grid: %s", e)
            return False

    @staticmethod
    def get_line_points(x1, y1, x2, y2):  # Bresenham's line algorithm
        points = []
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx = 1 if x1 < x2 else -1
        sy = 1 if y1 < y2 else -1
        err = dx - dy

        while True:
            points.append((x1, y1))
            if x1 == x2 and y1 == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy
                x1 += sx
            if e2 < dx:
                err += dx
                y1 += sy
        return points

    def generate(self):  # Generating complete dungeon
        logger.info("Starting dungeon generation...")

        # Generate rooms
        num_rooms = self.generate_rooms()
        if num_rooms == 0:
            raise RuntimeError("Failed to generate any rooms. Try adjusting parameters.")

        # Generate MST if we have enough rooms
        if num_rooms >= 3:
            if not self.generate_mst():
                logger.warning("MST generation failed, dungeon may not be connected")
        else:
            logger.warning(
                "Only %d rooms generated, skipping MST", num_rooms
            )

        # Generate grid
        if not self.generate_grid():
            raise RuntimeError("Failed to generate grid")

        logger.info(
            "Dungeon generation complete: %d rooms, %d corridors, %d doors",
            num_rooms,
            len(self.corridors),
            len(self.doors),
        )

        return self.rooms, self.corridors, self.doors, self.triangulation, self.grid
    