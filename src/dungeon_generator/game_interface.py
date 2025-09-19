import pygame
import sys
from .dungeon import DungeonGenerator
from .pathfinding import AStarPathfinder

class DungeonExplorer:
    def __init__(self, width=800, height=800, dungeon_width=100, dungeon_height=100):
        pygame.init()
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dungeon Explorer")

        self.dungeon_width = dungeon_width
        self.dungeon_height = dungeon_height
        self.cell_size = min(width // dungeon_width, height // dungeon_height)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        print("Generating dungeon...")
        self.dungeon = DungeonGenerator(dungeon_width, dungeon_height)
        self.rooms, _, _, _, self.grid = self.dungeon.generate()
        self.pathfinder = AStarPathfinder(self.grid)
        print("Dungeon generated.")

        self.player_x, self.player_y = int(self.rooms[0].center.x), int(self.rooms[0].center.y)
        self.path = None
        self.path_progress = 0.0
        self.path_speed = 5.0 # cells per second

        self.colors = {
            "background": (10, 10, 40),
            "floor": (50, 50, 80),
            "wall": (0, 0, 0),
            "player": (255, 100, 100),
            "path": (100, 200, 255, 100),
        }

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = pygame.mouse.get_pos()
                gx, gy = mx // self.cell_size, my // self.cell_size
                if 0 <= gx < self.dungeon_width and 0 <= gy < self.dungeon_height and self.grid[gy][gx] > 0:
                    self.path = self.pathfinder.find_path(self.player_x, self.player_y, gx, gy)
                    self.path_progress = 0
        return True

    def update(self, dt):
        if self.path and len(self.path) > 1:
            self.path_progress += self.path_speed * dt
            if self.path_progress >= 1.0:
                self.path_progress = 0
                self.player_x, self.player_y = self.path.pop(1)
            if len(self.path) <= 1:
                self.path = None

    def draw(self):
        self.screen.fill(self.colors["wall"])
        for y in range(self.dungeon_height):
            for x in range(self.dungeon_width):
                if self.grid[y][x] > 0:
                    r = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, self.colors["floor"], r)

        if self.path:
            path_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            for x, y in self.path:
                r = pygame.Rect(x * self.cell_size, y * self.cell_size, self.cell_size, self.cell_size)
                pygame.draw.rect(path_surface, self.colors["path"], r)
            self.screen.blit(path_surface, (0,0))
        
        player_rect = pygame.Rect(self.player_x * self.cell_size, self.player_y * self.cell_size, self.cell_size, self.cell_size)
        pygame.draw.rect(self.screen, self.colors["player"], player_rect)
        
        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self.handle_events()
            self.update(dt)
            self.draw()
        pygame.quit()
        sys.exit()