import heapq
import math


class Node:     # Represents A* pathfinding node    
    def __init__(self, x, y, cost=0.0, heuristic=0.0):  # Initializing node with position, cost, and heuristic
        self.x = x
        self.y = y
        self.cost = cost
        self.heuristic = heuristic
        self.parent = None

    @property
    def total(self):    # Total estimated cost (f = g + h)
        return self.cost + self.heuristic

    def __lt__(self, other):    # Less-than for priority queue based on total cost
        return self.total < other.total
    
    def __eq__(self, other):    # Equality based on position
        return self.x == other.x and self.y == other.y

    def __hash__(self):   # Hash based on position for use in sets and dictionaries
        return hash((self.x, self.y))


class AStarPathfinder:    
    def __init__(self, grid):   # Initializing pathfinder with a grid, 0 = wall, 1 = walkable
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

    def find_path(self, start_x, start_y, end_x, end_y):   # Find path from start to end using A* algorithm
        # Validate inputs
        if not (0 <= start_x < self.width and 0 <= start_y < self.height):
            return None
        if not (0 <= end_x < self.width and 0 <= end_y < self.height):
            return None
        if self.grid[start_y][start_x] == 0 or self.grid[end_y][end_x] == 0:
            return None

        start_node = Node(start_x, start_y, 0, 
                         self.heuristic(start_x, start_y, end_x, end_y))
        end_node = Node(end_x, end_y)

        open_set = [start_node]
        closed_set = set()
        open_dict = {(start_x, start_y): start_node}

        while open_set:
            current_node = heapq.heappop(open_set)
            del open_dict[(current_node.x, current_node.y)]

            if current_node == end_node:
                return self.reconstruct_path(current_node)

            closed_set.add((current_node.x, current_node.y))

            # 8-directional movement
            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), 
                          (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                nx, ny = current_node.x + dx, current_node.y + dy

                # Checking bounds and walkability
                if not (0 <= nx < self.width and 0 <= ny < self.height):
                    continue
                if self.grid[ny][nx] == 0:
                    continue
                if (nx, ny) in closed_set:
                    continue
                
                # Calculating cost (diagonal moves cost more)
                move_cost = 1.414 if dx != 0 and dy != 0 else 1.0
                new_cost = current_node.cost + move_cost
                
                # Check if this path to neighbor is better
                if (nx, ny) in open_dict:
                    existing_node = open_dict[(nx, ny)]
                    if new_cost < existing_node.cost:
                        existing_node.cost = new_cost
                        existing_node.parent = current_node
                        heapq.heapify(open_set)
                else:
                    neighbor = Node(nx, ny)
                    neighbor.cost = new_cost
                    neighbor.heuristic = self.heuristic(nx, ny, end_x, end_y)
                    neighbor.parent = current_node
                    heapq.heappush(open_set, neighbor)
                    open_dict[(nx, ny)] = neighbor

        return None  # No path found

    def heuristic(self, x1, y1, x2, y2):   # Euclidean distance heuristic between two points; first point (x1, y1), second point (x2, y2)
        return math.hypot(x2 - x1, y2 - y1)

    def reconstruct_path(self, node):   # Reconstruct path from end node to start node
        path = []
        while node:
            path.append((node.x, node.y))
            node = node.parent
        return list(reversed(path))