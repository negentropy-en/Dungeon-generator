import unittest
import random
import math

from dungeon_generator.delaunay import Point, Triangle, DelaunayTriangulation
from dungeon_generator.dungeon import Room, DungeonGenerator
from dungeon_generator.pathfinding import Node, AStarPathfinder


class TestPoint(unittest.TestCase):    
    def test_point_creation(self):  # Test basic point creation
        p = Point(3, 4)
        self.assertEqual(p.x, 3)
        self.assertEqual(p.y, 4)
    
    def test_point_equality(self):  # Test point equality and inequality
        p1 = Point(1, 2)
        p2 = Point(1, 2)
        p3 = Point(2, 1)
        self.assertEqual(p1, p2)
        self.assertNotEqual(p1, p3)
    
    def test_point_hash(self):  # Test point hashing for use in sets/dicts
        p1 = Point(1, 2)
        p2 = Point(1, 2)
        p3 = Point(2, 1)
        point_set = {p1, p2, p3}
        self.assertEqual(len(point_set), 2)
    
    def test_point_repr(self):  # String representation of Point
        p = Point(5, 10)
        self.assertEqual(repr(p), "Point(5, 10)")


class TestTriangle(unittest.TestCase):    # Testing Triangle class functionality    
    def test_triangle_creation(self):   # Basic triangle creation
        p1 = Point(0, 0)
        p2 = Point(4, 0)
        p3 = Point(2, 3)
        t = Triangle(p1, p2, p3)
        self.assertEqual(len(t.vertices), 3)
        self.assertEqual(len(t.edges), 3)
    
    def test_circumcircle_right_triangle(self): # Test circumcircle for right triangle
        p1 = Point(0, 0)
        p2 = Point(2, 0)
        p3 = Point(0, 2)
        t = Triangle(p1, p2, p3)
        
        center, radius = t.circumcircle
        self.assertAlmostEqual(center[0], 1.0, places=5)
        self.assertAlmostEqual(center[1], 1.0, places=5)
        self.assertAlmostEqual(radius, math.sqrt(2), places=5)
    
    def test_circumcircle_equilateral(self):    # Test circumcircle for equilateral triangle
        p1 = Point(0, 0)
        p2 = Point(2, 0)
        p3 = Point(1, math.sqrt(3))
        t = Triangle(p1, p2, p3)
        
        center, radius = t.circumcircle
        self.assertAlmostEqual(center[0], 1.0, places=5)
        self.assertAlmostEqual(center[1], math.sqrt(3) / 3, places=5)
    
    def test_degenerate_triangle(self):   # Test circumcircle for degenerate triangle (collinear points)
        p1 = Point(0, 0)
        p2 = Point(1, 1)
        p3 = Point(2, 2)
        t = Triangle(p1, p2, p3)
        
        center, radius = t.circumcircle
        self.assertIsNone(center[0])
        self.assertEqual(radius, float('inf'))
    
    def test_point_in_circumcircle(self):   # Test point inside circumcircle
        p1 = Point(0, 0)
        p2 = Point(2, 0)
        p3 = Point(0, 2)
        t = Triangle(p1, p2, p3)
        
        p_inside = Point(1, 1)
        self.assertTrue(t.in_circumcircle(p_inside))
        
        p_outside = Point(3, 3)
        self.assertFalse(t.in_circumcircle(p_outside))
    
    def test_point_on_circumcircle_boundary(self):  # Test point exactly on boundary is not considered inside
        p1 = Point(0, 0)
        p2 = Point(2, 0)
        p3 = Point(0, 2)
        t = Triangle(p1, p2, p3)
        
        p_on = Point(2, 2)
        self.assertFalse(t.in_circumcircle(p_on))


class TestDelaunayTriangulation(unittest.TestCase):    # Testing Delaunay triangulation functionality
    def test_minimum_points_requirement(self):    # Test that triangulation requires at least 3 points
        with self.assertRaises(ValueError):
            DelaunayTriangulation([])
        
        with self.assertRaises(ValueError):
            DelaunayTriangulation([Point(0, 0)])
        
        with self.assertRaises(ValueError):
            DelaunayTriangulation([Point(0, 0), Point(1, 1)])
    
    def test_simple_triangle(self): # Test triangulation of 3 points creates 1 triangle
        points = [Point(0, 0), Point(4, 0), Point(2, 3)]
        dt = DelaunayTriangulation(points)
        
        self.assertEqual(len(dt.triangles), 1)
        self.assertEqual(len(dt.triangles[0].vertices), 3)
    
    def test_square_triangulation(self):    # Test triangulation of 4 points forming a square creates 2 triangles
        points = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
        dt = DelaunayTriangulation(points)
        
        self.assertEqual(len(dt.triangles), 2)
    
    def test_all_points_covered(self):  # Test that all input points are vertices in the triangulation
        points = [Point(0, 0), Point(10, 0), Point(10, 10), Point(0, 10)]
        dt = DelaunayTriangulation(points)
        
        final_vertices = set()
        for triangle in dt.triangles:
            final_vertices.update(triangle.vertices)
        
        self.assertEqual(set(points), final_vertices)
    
    def test_delaunay_property(self):   # Test that no point lies within the circumcircle of any triangle
        points = [
            Point(0, 0), Point(5, 0), Point(5, 5), Point(0, 5),
            Point(2.5, 2.5)
        ]
        dt = DelaunayTriangulation(points)
        
        for triangle in dt.triangles:
            for point in points:
                if point not in triangle.vertices:
                    self.assertFalse(
                        triangle.in_circumcircle(point),
                        f"Delaunay property violated: {point} inside circumcircle"
                    )

class TestRoom(unittest.TestCase):  #  Testing Room class functionality
    def test_room_creation(self):   # Test basic room creation
        room = Room(10, 20, 5, 8, 0)
        self.assertEqual(room.x, 10)
        self.assertEqual(room.y, 20)
        self.assertEqual(room.width, 5)
        self.assertEqual(room.height, 8)
        self.assertEqual(room.id, 0)
    
    def test_room_center(self):  # Test center point calculation
        room = Room(0, 0, 10, 10, 0)
        self.assertEqual(room.center.x, 5)
        self.assertEqual(room.center.y, 5)
    
    def test_room_intersection_positive(self):  # Test that overlapping rooms are detected as intersecting
        room1 = Room(0, 0, 10, 10, 0)
        room2 = Room(5, 5, 10, 10, 1)
        self.assertTrue(room1.intersects(room2))
        self.assertTrue(room2.intersects(room1))
    
    def test_room_intersection_negative(self):  # Test that non-overlapping rooms are not intersecting
        room1 = Room(0, 0, 5, 5, 1)
        room2 = Room(10, 0, 5, 5, 2)
        self.assertFalse(room1.intersects(room2))
        self.assertFalse(room2.intersects(room1))
    
    def test_room_edge_touching(self):  # Test that rooms touching at edges are considered intersecting
        room1 = Room(0, 0, 10, 10, 0)
        room2 = Room(10, 0, 10, 10, 1)
        self.assertTrue(room1.intersects(room2))
    
    def test_contains_point(self):  # Test point containment within room
        room = Room(10, 10, 10, 10, 0)
        self.assertTrue(room.contains_point(15, 15))
        self.assertTrue(room.contains_point(10, 10))
        self.assertTrue(room.contains_point(20, 20))
        self.assertFalse(room.contains_point(5, 5))

class TestDungeonGenerator(unittest.TestCase):  # Testing DungeonGenerator class functionality    
    def test_generator_creation(self):    # Test basic generator creation with valid parameters
        gen = DungeonGenerator(width=50, height=50, max_rooms=10)
        self.assertEqual(gen.width, 50)
        self.assertEqual(gen.height, 50)
        self.assertEqual(gen.max_rooms, 10)
    
    def test_parameter_validation(self):    # Test that invalid parameters raise ValueError
        with self.assertRaises(ValueError):
            DungeonGenerator(width=5, height=50)
        
        with self.assertRaises(ValueError):
            DungeonGenerator(width=50, height=50, max_rooms=0)
        
        with self.assertRaises(ValueError):
            DungeonGenerator(width=50, height=50, min_room_size=10, max_room_size=5)
    
    def test_room_generation_respects_max(self):    # Test that generated room count does not exceed max_rooms
        gen = DungeonGenerator(width=100, height=100, max_rooms=5)
        gen.generate_rooms()
        self.assertLessEqual(len(gen.rooms), 5)
    
    def test_rooms_dont_overlap(self):   # Test that generated rooms do not overlap
        gen = DungeonGenerator(width=100, height=100, max_rooms=10)
        gen.generate_rooms()
        
        for i, room1 in enumerate(gen.rooms):
            for room2 in gen.rooms[i+1:]:
                self.assertFalse(
                    room1.intersects(room2),
                    f"Rooms {room1.id} and {room2.id} overlap"
                )
    
    def test_rooms_within_bounds(self):  # Test that all rooms are within dungeon bounds
        gen = DungeonGenerator(width=50, height=50, max_rooms=10)
        gen.generate_rooms()
        
        for room in gen.rooms:
            self.assertGreaterEqual(room.x, 1)
            self.assertGreaterEqual(room.y, 1)
            self.assertLessEqual(room.x + room.width, gen.width - 1)
            self.assertLessEqual(room.y + room.height, gen.height - 1)
    
    def test_delaunay_generation(self):  # Test that Delaunay triangulation is created correctly
        gen = DungeonGenerator(width=100, height=100, max_rooms=10)
        gen.generate_rooms()
        
        if len(gen.rooms) >= 3:
            result = gen.generate_delaunay()
            self.assertTrue(result)
            self.assertIsNotNone(gen.triangulation)
            self.assertGreater(len(gen.triangulation.triangles), 0)
    
    def test_mst_creates_connections(self): # Test that MST creates connections between rooms
        random.seed(42)
        gen = DungeonGenerator(width=100, height=100, max_rooms=10)
        gen.generate_rooms()
        
        if len(gen.rooms) >= 3:
            gen.generate_mst()
            total_connections = sum(len(room.connections) for room in gen.rooms)
            self.assertGreater(total_connections, 0)
            
    def test_mst_connectivity(self):    # Test that MST connects all rooms together
        random.seed(42)
        gen = DungeonGenerator(width=200, height=200, max_rooms=15)
        gen.generate_rooms()
        
        if len(gen.rooms) >= 3:
            gen.generate_mst()
            
            adj_list = {room.id: room.connections for room in gen.rooms}
            start_node = gen.rooms[0].id
            queue = [start_node]
            visited = {start_node}
            
            while queue:
                current_id = queue.pop(0)
                for neighbor_id in adj_list.get(current_id, []):
                    if neighbor_id not in visited:
                        visited.add(neighbor_id)
                        queue.append(neighbor_id)
            
            self.assertEqual(len(visited), len(gen.rooms), "MST did not connect all rooms")
    
    def test_grid_generation(self):   # Test that grid is generated correctly
        gen = DungeonGenerator(width=50, height=40, max_rooms=5)
        gen.generate_rooms()
        result = gen.generate_grid()
        
        self.assertTrue(result)
        self.assertEqual(len(gen.grid), 40)
        self.assertEqual(len(gen.grid[0]), 50)
    
    def test_full_generation(self): # Test full dungeon generation process
        random.seed(123)
        gen = DungeonGenerator(width=100, height=100, max_rooms=15)
        rooms, corridors, doors, triangulation, grid = gen.generate()
        
        self.assertIsInstance(corridors, list)
        self.assertIsInstance(doors, list)
        self.assertIsNotNone(rooms)
        self.assertIsNotNone(grid)
        self.assertGreater(len(rooms), 0)
        self.assertEqual(len(grid), 100)
        self.assertEqual(len(grid[0]), 100)
        if len(rooms) >= 3 and triangulation is not None:
            self.assertGreater(len(triangulation.triangles), 0)


class TestNode(unittest.TestCase):  # Testing Node class for pathfinding    
    def test_node_creation(self):   # Test basic node creation
        node = Node(5, 10, cost=2.0, heuristic=3.0)
        self.assertEqual(node.x, 5)
        self.assertEqual(node.y, 10)
        self.assertEqual(node.cost, 2.0)
        self.assertEqual(node.heuristic, 3.0)
    
    def test_node_total(self):  # Test total cost calculation
        node = Node(0, 0, cost=2.5, heuristic=3.5)
        self.assertEqual(node.total, 6.0)
    
    def test_node_comparison(self): # Test node comparison based on total cost
        node1 = Node(0, 0, cost=2.0, heuristic=3.0)
        node2 = Node(1, 1, cost=3.0, heuristic=1.0)
        self.assertFalse(node1 < node2)
        self.assertTrue(node2 < node1)
    
    def test_node_equality(self):   # Test node equality and inequality
        node1 = Node(5, 10)
        node2 = Node(5, 10)
        node3 = Node(5, 11)
        self.assertEqual(node1, node2)
        self.assertNotEqual(node1, node3)
        
    def test_node_hash(self):   # Test node hashing for use in sets/dicts
        node1 = Node(5, 10)
        node2 = Node(5, 10)
        node3 = Node(5, 11)
        node_set = {node1, node2, node3}
        self.assertEqual(len(node_set), 2)


class TestAStarPathfinder(unittest.TestCase):   # Testing A* pathfinding algorithm    
    def setUp(self):    # Setting up common grids for pathfinding tests
        self.open_grid = [
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1],
            [1, 1, 1, 1, 1]
        ]
        
        self.wall_grid = [
            [1, 1, 1, 1, 0],
            [0, 0, 1, 1, 0],
            [1, 1, 1, 0, 0],
            [1, 0, 1, 1, 1],
            [1, 1, 1, 0, 1]
        ]
        
        self.blocked_grid = [
            [1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1],
            [1, 1, 0, 1, 1]
        ]
    
    def test_pathfinder_creation(self):  # Test basic pathfinder creation
        pf = AStarPathfinder(self.open_grid)
        self.assertEqual(pf.width, 5)
        self.assertEqual(pf.height, 5)
    
    def test_simple_path(self):  # Test simple straight pathfinding
        pf = AStarPathfinder(self.open_grid)
        path = pf.find_path(0, 0, 2, 2)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (2, 2))
        self.assertGreater(len(path), 1)
    
    def test_diagonal_path(self):   # Test diagonal pathfinding
        pf = AStarPathfinder(self.open_grid)
        path = pf.find_path(0, 0, 4, 4)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[0], (0, 0))
        self.assertEqual(path[-1], (4, 4))
        self.assertEqual(len(path), 5)
    
    def test_path_with_obstacle(self):  # Test pathfinding around obstacles
        pf = AStarPathfinder(self.wall_grid)
        path = pf.find_path(0, 0, 4, 4)
        
        self.assertIsNotNone(path)
        self.assertEqual(path[-1], (4, 4))
        for x, y in path:
            self.assertEqual(self.wall_grid[y][x], 1, f"Path goes through wall at ({x}, {y})")
    
    def test_no_path_found(self):   # Test pathfinding when no path exists
        pf = AStarPathfinder(self.blocked_grid)
        path = pf.find_path(0, 0, 4, 0)
        self.assertIsNone(path)
    
    def test_invalid_start_position(self):   # Test pathfinding with invalid start position
        pf = AStarPathfinder(self.wall_grid)
        path = pf.find_path(0, 1, 4, 4)
        self.assertIsNone(path)
    
    def test_invalid_end_position(self):    # Test pathfinding with invalid end position
        pf = AStarPathfinder(self.wall_grid)
        path = pf.find_path(0, 0, 4, 0)
        self.assertIsNone(path)
    
    def test_out_of_bounds(self):   # Test pathfinding with out-of-bounds coordinates
        pf = AStarPathfinder(self.open_grid)
        
        path = pf.find_path(-1, 0, 2, 2)
        self.assertIsNone(path)
        
        path = pf.find_path(0, 0, 10, 10)
        self.assertIsNone(path)
    
    def test_start_equals_end(self):    # Test pathfinding when start and end positions are the same
        pf = AStarPathfinder(self.open_grid)
        path = pf.find_path(2, 2, 2, 2)
        
        self.assertIsNotNone(path)
        self.assertEqual(len(path), 1)
        self.assertEqual(path[0], (2, 2))
    
    def test_path_continuity(self):  # Test that path consists of continuous steps
        pf = AStarPathfinder(self.open_grid)
        path = pf.find_path(0, 0, 4, 4)
        
        for i in range(len(path) - 1):
            x1, y1 = path[i]
            x2, y2 = path[i + 1]
            self.assertLessEqual(abs(x2 - x1), 1)
            self.assertLessEqual(abs(y2 - y1), 1)
            self.assertTrue(x2 != x1 or y2 != y1)
    
    def test_heuristic_calculation(self):   # Test heuristic calculation (Euclidean distance)
        pf = AStarPathfinder(self.open_grid)
        h = pf.heuristic(0, 0, 3, 4)
        self.assertAlmostEqual(h, 5.0, places=5)


class TestIntegration(unittest.TestCase):  # Integration tests for dungeon generation and pathfinding    
    def test_full_dungeon_generation_and_pathfinding(self): # Test full dungeon generation and pathfinding between rooms
        random.seed(42)
        gen = DungeonGenerator(width=50, height=50, max_rooms=10)
        rooms, corridors, doors, triangulation, grid = gen.generate()
        
        self.assertIsInstance(corridors, list)
        self.assertIsInstance(doors, list)
        
        if len(rooms) >= 2:
            self.assertGreaterEqual(len(corridors), 1)
            for path in corridors:
                self.assertIsInstance(path, list)
                self.assertGreaterEqual(len(path), 2)
                for step in path:
                    self.assertIsInstance(step, tuple)
                    self.assertEqual(len(step), 2)
                    
        if len(rooms) >= 3 and triangulation is not None:
            self.assertGreater(len(triangulation.triangles), 0)
            pf = AStarPathfinder(grid)
            start_x = int(rooms[0].center.x)
            start_y = int(rooms[0].center.y)
            end_x = int(rooms[1].center.x)
            end_y = int(rooms[1].center.y)
            
            path = pf.find_path(start_x, start_y, end_x, end_y)
            
            self.assertIsNotNone(path)
            self.assertEqual(path[0], (start_x, start_y))
            self.assertEqual(path[-1], (end_x, end_y))
    
    def test_reproducible_generation_with_seed(self):   # Test that using the same seed produces the same dungeon layout
        random.seed(12345)
        gen1 = DungeonGenerator(width=60, height=60, max_rooms=8)
        rooms1, _, _, _, _ = gen1.generate()
        
        random.seed(12345)
        gen2 = DungeonGenerator(width=60, height=60, max_rooms=8)
        rooms2, _, _, _, _ = gen2.generate()
        
        self.assertEqual(len(rooms1), len(rooms2))
        
        for r1, r2 in zip(rooms1, rooms2):
            self.assertEqual(r1.x, r2.x)
            self.assertEqual(r1.y, r2.y)
            self.assertEqual(r1.width, r2.width)
            self.assertEqual(r1.height, r2.height)
    
    def test_path_between_all_rooms(self):  # Test pathfinding between all pairs of rooms in the generated dungeon
        random.seed(999)
        gen = DungeonGenerator(width=100, height=100, max_rooms=8)
        rooms, _, _, _, grid = gen.generate()
        
        if len(rooms) < 2:
            self.skipTest("Not enough rooms generated")
        
        pf = AStarPathfinder(grid)
        start_x = int(rooms[0].center.x)
        start_y = int(rooms[0].center.y)
        
        for room in rooms[1:]:
            end_x = int(room.center.x)
            end_y = int(room.center.y)
            
            path = pf.find_path(start_x, start_y, end_x, end_y)
            self.assertIsNotNone(path, f"No path from room 0 to room {room.id}")
    
    def test_random_room_count_generation(self):    # Test dungeon generation with random room counts
        for _ in range(3):
            target_rooms = random.randint(3, 100)
            gen = DungeonGenerator(width=150, height=150, max_rooms=target_rooms)
            rooms, _, _, _, _ = gen.generate()
            
            self.assertGreater(len(rooms), 0)
            self.assertLessEqual(len(rooms), target_rooms)


class TestBresenhamLine(unittest.TestCase): # Testing Bresenham's line algorithm    
    def test_horizontal_line(self):   # Test horizontal line generation
        points = list(DungeonGenerator.get_line_points(1, 1, 5, 1))
        self.assertEqual(points[0], (1, 1))
        self.assertEqual(points[-1], (5, 1))
        self.assertEqual(len(points), 5)
    
    def test_vertical_line(self):   # Test vertical line generation
        points = list(DungeonGenerator.get_line_points(0, 0, 0, 5))
        self.assertEqual(points[0], (0, 0))
        self.assertEqual(points[-1], (0, 5))
        self.assertEqual(len(points), 6)
    
    def test_diagonal_line(self):   # Test diagonal line generation
        points = list(DungeonGenerator.get_line_points(0, 0, 3, 3))
        self.assertGreater(len(points), 0)
        self.assertEqual(points[0], (0, 0))
        self.assertEqual(points[-1], (3, 3))


class TestEdgeCases(unittest.TestCase):  # Testing edge cases in dungeon generation    
    def test_tiny_dungeon(self):    # Test generation of a very small dungeon
        gen = DungeonGenerator(width=10, height=10, max_rooms=3, 
                               min_room_size=3, max_room_size=4)
        rooms, _, _, _, grid = gen.generate()
        
        self.assertGreater(len(rooms), 0)
        self.assertIsNotNone(grid)
    
    def test_large_rooms_small_dungeon(self):   # Test generation when room sizes are large relative to dungeon size
        gen = DungeonGenerator(width=30, height=30, max_rooms=5,
                               min_room_size=8, max_room_size=12)
        rooms, _, _, _, grid = gen.generate()
        
        self.assertGreater(len(rooms), 0)