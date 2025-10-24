import math


class Point:  # Represents a 2D point
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):  # Equality based on coordinates
        return self.x == other.x and self.y == other.y

    def __hash__(self):  # Hash based on coordinates for use in sets and dictionaries
        return hash((self.x, self.y))

    def __repr__(self):  # String representation for debugging
        return f"Point({self.x}, {self.y})"


class Triangle:  # Represents a triangle defined by three points
    def __init__(self, a, b, c):
        self.vertices = [a, b, c]
        self.edges = [(a, b), (b, c), (c, a)]
        self.circumcircle = self.calculate_circumcircle()

    def calculate_circumcircle(self):  # Calculate circumcircle (center and radius)
        point_a, point_b, point_c = self.vertices
        determinant = 2 * (
            point_a.x * (point_b.y - point_c.y)
            + point_b.x * (point_c.y - point_a.y)
            + point_c.x * (point_a.y - point_b.y)
        )

        if abs(determinant) < 1e-10:  # Numerical stability check
            return (None, None), float("inf")

        ux = (
            (point_a.x ** 2 + point_a.y ** 2) * (point_b.y - point_c.y)
            + (point_b.x ** 2 + point_b.y ** 2) * (point_c.y - point_a.y)
            + (point_c.x ** 2 + point_c.y ** 2) * (point_a.y - point_b.y)
        ) / determinant
        uy = (
            (point_a.x ** 2 + point_a.y ** 2) * (point_c.x - point_b.x)
            + (point_b.x ** 2 + point_b.y ** 2) * (point_a.x - point_c.x)
            + (point_c.x ** 2 + point_c.y ** 2) * (point_b.x - point_a.x)
        ) / determinant

        radius = math.hypot(point_a.x - ux, point_a.y - uy)
        return (ux, uy), radius

    def in_circumcircle(self, point):  # Check if a point is inside circumcircle
        center, radius = self.circumcircle
        if center[0] is None:
            return False

        dist = math.hypot(point.x - center[0], point.y - center[1])
        # Using strict inequality with epsilon for Delaunay property
        return dist < radius - 1e-10


class DelaunayTriangulation:  # Delaunay triangulation using Bowyer-Watson
    def __init__(self, points):  # Initializing triangulation with a list of points
        if not points or len(points) < 3:
            raise ValueError("Delaunay triangulation requires at least 3 points")

        self.points = points
        self.triangles = []
        self.super_triangle = self.create_super_triangle()
        self.triangulate()

    def create_super_triangle(self):  # Create a super-triangle
        x_coords = [p.x for p in self.points]
        y_coords = [p.y for p in self.points]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        dx = max_x - min_x
        dy = max_y - min_y
        margin = max(dx, dy) * 2
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2

        # Create a triangle that encompasses all points
        p1 = Point(center_x - margin, center_y - margin)
        p2 = Point(center_x + margin, center_y - margin)
        p3 = Point(center_x, center_y + margin * 1.5)

        return Triangle(p1, p2, p3)

    def triangulate(self):  # Performing the Bowyer-Watson triangulation algorithm
        self.triangles = [self.super_triangle]

        for point in self.points:
            bad_triangles = []
            for triangle in self.triangles:
                if triangle.in_circumcircle(point):
                    bad_triangles.append(triangle)

            # Find boundary of polygonal hole
            polygon = []
            for triangle in bad_triangles:
                for edge in triangle.edges:
                    is_shared = False
                    for other in bad_triangles:
                        if triangle is other:
                            continue
                        # Check both orientations of the edge
                        if edge in other.edges or (edge[1], edge[0]) in other.edges:
                            is_shared = True
                            break
                    if not is_shared:
                        polygon.append(edge)

            # Remove bad triangles
            for triangle in bad_triangles:
                self.triangles.remove(triangle)

            # Re-triangulate the polygonal hole
            for edge in polygon:
                new_triangle = Triangle(edge[0], edge[1], point)
                self.triangles.append(new_triangle)

        # Remove triangles that share vertices with super-triangle
        st_vertices = set(self.super_triangle.vertices)
        self.triangles = [
            t for t in self.triangles if not any(v in st_vertices for v in t.vertices)
        ]
        