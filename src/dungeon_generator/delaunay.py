import math

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y
    def __hash__(self):
        return hash((self.x, self.y))
    def __repr__(self):
        return f"Point({self.x}, {self.y})"

class Triangle:
    def __init__(self, a, b, c):
        self.vertices = [a, b, c]
        self.edges = [(a, b), (b, c), (c, a)]
        self.circumcircle = self.calculate_circumcircle()

    def calculate_circumcircle(self):
        A, B, C = self.vertices
        D = 2 * (A.x * (B.y - C.y) + B.x * (C.y - A.y) + C.x * (A.y - B.y))
        if D == 0:
            return (None, None), float("inf")
        ux = ((A.x**2 + A.y**2) * (B.y - C.y) +
              (B.x**2 + B.y**2) * (C.y - A.y) +
              (C.x**2 + C.y**2) * (A.y - B.y)) / D
        uy = ((A.x**2 + A.y**2) * (C.x - B.x) +
              (B.x**2 + B.y**2) * (A.x - C.x) +
              (C.x**2 + C.y**2) * (B.x - A.x)) / D
        radius = math.hypot(A.x - ux, A.y - uy)
        return (ux, uy), radius

    def in_circumcircle(self, point):
        center, radius = self.circumcircle
        if center[0] is None:
            return False
        return math.hypot(point.x - center[0], point.y - center[1]) <= radius

class DelaunayTriangulation:
    def __init__(self, points):
        self.points = points
        self.triangles = []
        self.super_triangle = self.create_super_triangle()
        self.triangulate()

    def create_super_triangle(self):
        x_coords = [p.x for p in self.points]
        y_coords = [p.y for p in self.points]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        dx = max_x - min_x
        dy = max_y - min_y
        margin = max(dx, dy) * 2
        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        
        p1 = Point(center_x - margin, center_y - margin)
        p2 = Point(center_x + margin, center_y - margin)
        p3 = Point(center_x, center_y + margin)
        
        return Triangle(p1, p2, p3)

    def triangulate(self):
        self.triangles = [self.super_triangle]
        for point in self.points:
            bad_triangles = []
            for t in self.triangles:
                if t.in_circumcircle(point):
                    bad_triangles.append(t)
            
            polygon = []
            for t in bad_triangles:
                for edge in t.edges:
                    is_shared = False
                    for other in bad_triangles:
                        if t is other:
                            continue
                        if edge in other.edges or (edge[1], edge[0]) in other.edges:
                            is_shared = True
                            break
                    if not is_shared:
                        polygon.append(edge)

            for t in bad_triangles:
                self.triangles.remove(t)

            for edge in polygon:
                new_triangle = Triangle(edge[0], edge[1], point)
                self.triangles.append(new_triangle)

        st_vertices = set(self.super_triangle.vertices)
        self.triangles = [t for t in self.triangles if not any(v in st_vertices for v in t.vertices)]