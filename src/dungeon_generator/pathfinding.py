import heapq
import math

class Node:
    def __init__(self, x, y, cost=0.0, heuristic=0.0):
        self.x = x
        self.y = y
        self.cost = cost
        self.heuristic = heuristic
        self.parent = None

    @property
    def total(self):
        return self.cost + self.heuristic

    def __lt__(self, other):
        return self.total < other.total
    
    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

class AStarPathfinder:
    def __init__(self, grid):
        self.grid = grid
        self.height = len(grid)
        self.width = len(grid[0]) if self.height > 0 else 0

    def find_path(self, start_x, start_y, end_x, end_y):
        start_node = Node(start_x, start_y, 0, self.heuristic(start_x, start_y, end_x, end_y))
        end_node = Node(end_x, end_y)

        open_set = [start_node]
        closed_set = set()

        while open_set:
            current_node = heapq.heappop(open_set)

            if current_node == end_node:
                return self.reconstruct_path(current_node)

            closed_set.add(current_node)

            for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0), (1, 1), (-1, -1), (1, -1), (-1, 1)]:
                nx, ny = current_node.x + dx, current_node.y + dy

                if not (0 <= nx < self.width and 0 <= ny < self.height) or self.grid[ny][nx] == 0:
                    continue

                neighbor = Node(nx, ny)
                if neighbor in closed_set:
                    continue
                
                move_cost = 1.414 if dx != 0 and dy != 0 else 1.0
                new_cost = current_node.cost + move_cost
                
                is_in_open_set = False
                for open_node in open_set:
                    if open_node == neighbor and new_cost >= open_node.cost:
                        is_in_open_set = True
                        break
                if is_in_open_set:
                    continue

                neighbor.cost = new_cost
                neighbor.heuristic = self.heuristic(nx, ny, end_x, end_y)
                neighbor.parent = current_node
                heapq.heappush(open_set, neighbor)

        return None  # No path found

    def heuristic(self, x1, y1, x2, y2):
        return math.hypot(x2 - x1, y2 - y1)

    def reconstruct_path(self, node):
        path = []
        while node:
            path.append((node.x, node.y))
            node = node.parent
        return list(reversed(path))