import random
import math
from .delaunay import Point, DelaunayTriangulation

class Room:
    def __init__(self, x, y, width, height, id):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.center = Point(x + width / 2, y + height / 2)
        self.id = id
        self.connections = []
        self.doors = []

    def intersects(self, other):
        return (self.x <= other.x + other.width and
                self.x + self.width >= other.x and
                self.y <= other.y + other.height and
                self.y + self.height >= other.y)

    def contains_point(self, x, y):
        return (self.x <= x <= self.x + self.width and
                self.y <= y <= self.y + self.height)

    def __repr__(self):
        return f"Room({self.id}: {self.x}, {self.y}, {self.width}, {self.height})"

class Door:
    def __init__(self, x, y, room1, room2):
        self.x = x
        self.y = y
        self.room1 = room1
        self.room2 = room2

    def __repr__(self):
        return f"Door({self.x}, {self.y})"

class DungeonGenerator:
    def __init__(self, width=100, height=100, max_rooms=15, min_room_size=5, max_room_size=15):
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

    def generate_rooms(self):
        for i in range(self.max_rooms * 5): # Try more times to get more rooms
            if len(self.rooms) >= self.max_rooms:
                break
            w = random.randint(self.min_room_size, self.max_room_size)
            h = random.randint(self.min_room_size, self.max_room_size)
            x = random.randint(1, self.width - w - 1)
            y = random.randint(1, self.height - h - 1)
            new_room = Room(x, y, w, h, len(self.rooms))
            if any(new_room.intersects(other_room) for other_room in self.rooms):
                continue
            self.rooms.append(new_room)

    def generate_delaunay(self):
        if len(self.rooms) < 3:
            self.triangulation = None
            return
        points = [room.center for room in self.rooms]
        self.triangulation = DelaunayTriangulation(points)

    def generate_mst(self):
        if not self.triangulation:
            self.generate_delaunay()
        if not self.triangulation:
            return

        all_edges = set()
        for triangle in self.triangulation.triangles:
            room_map = {r.center: r for r in self.rooms}
            
            p1, p2, p3 = triangle.vertices
            r1, r2, r3 = room_map.get(p1), room_map.get(p2), room_map.get(p3)

            if r1 and r2:
                dist = math.hypot(r1.center.x - r2.center.x, r1.center.y - r2.center.y)
                all_edges.add(tuple(sorted((r1.id, r2.id)) + [dist]))
            if r2 and r3:
                dist = math.hypot(r2.center.x - r3.center.x, r2.center.y - r3.center.y)
                all_edges.add(tuple(sorted((r2.id, r3.id)) + [dist]))
            if r3 and r1:
                dist = math.hypot(r3.center.x - r1.center.x, r3.center.y - r1.center.y)
                all_edges.add(tuple(sorted((r3.id, r1.id)) + [dist]))

        sorted_edges = sorted(list(all_edges), key=lambda item: item[2])
        
        parent = list(range(len(self.rooms)))
        def find(i):
            if parent[i] == i:
                return i
            parent[i] = find(parent[i])
            return parent[i]

        def union(i, j):
            root_i = find(i)
            root_j = find(j)
            if root_i != root_j:
                parent[root_j] = root_i
                return True
            return False

        mst_edges = []
        for u, v, w in sorted_edges:
            if union(u, v):
                mst_edges.append((self.rooms[u], self.rooms[v]))
        
        # Add a few extra edges back for loops
        num_extra_edges = int(len(mst_edges) * 0.2) # Add 20% extra edges
        potential_extra_edges = [
            (self.rooms[u], self.rooms[v]) for u, v, w in sorted_edges 
            if (self.rooms[u], self.rooms[v]) not in mst_edges and (self.rooms[v], self.rooms[u]) not in mst_edges
        ]
        random.shuffle(potential_extra_edges)
        
        final_edges = mst_edges + potential_extra_edges[:num_extra_edges]

        for room1, room2 in final_edges:
            room1.connections.append(room2.id)
            room2.connections.append(room1.id)
            self.create_corridor_between_rooms(room1, room2)

    def create_corridor_between_rooms(self, room1, room2):
        x1, y1 = int(room1.center.x), int(room1.center.y)
        x2, y2 = int(room2.center.x), int(room2.center.y)
        
        path = []
        if random.choice([True, False]): # Horizontal then vertical
            path.append((x1, y1))
            path.append((x2, y1))
            path.append((x2, y2))
        else: # Vertical then horizontal
            path.append((x1, y1))
            path.append((x1, y2))
            path.append((x2, y2))
        
        self.corridors.append(path)

    def generate_grid(self):
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        for room in self.rooms:
            for y in range(room.y, room.y + room.height):
                for x in range(room.x, room.x + room.width):
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.grid[y][x] = 1 # Room floor
        
        for corridor in self.corridors:
            for i in range(len(corridor) - 1):
                x1, y1 = corridor[i]
                x2, y2 = corridor[i + 1]
                for x, y in self.get_line_points(int(x1), int(y1), int(x2), int(y2)):
                    if 0 <= y < self.height and 0 <= x < self.width:
                        self.grid[y][x] = 1 # Mark corridor as floor too

    @staticmethod
    def get_line_points(x1, y1, x2, y2):
        points = []
        dx, dy = abs(x2 - x1), abs(y2 - y1)
        sx, sy = 1 if x1 < x2 else -1, 1 if y1 < y2 else -1
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

    def generate(self):
        self.generate_rooms()
        self.generate_mst()
        self.generate_grid()
        return self.rooms, self.corridors, self.doors, self.triangulation, self.grid