import sys
import pygame
from .dungeon import DungeonGenerator
from .pathfinding import AStarPathfinder


class DungeonExplorer:    
    def __init__(self, width=800, height=800, dungeon_width=100, dungeon_height=100):   # Initializing the dungeon explorer interface
    # width: Screen width in pixels
    # height: Screen height in pixels
    # dungeon_width: Dungeon grid width
    # dungeon_height: Dungeon grid height
    # runtime error if generation fails
    
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

        # Generate dungeon with error handling
        print("Generating dungeon...")
        try:
            self.dungeon = DungeonGenerator(dungeon_width, dungeon_height)
            self.rooms, _, _, _, self.grid = self.dungeon.generate()
            
            if not self.rooms:
                raise RuntimeError("No rooms generated - dungeon is empty")
                
            self.pathfinder = AStarPathfinder(self.grid)
            print(f"Dungeon generated with {len(self.rooms)} rooms.")
            
        except Exception as e:
            print(f"Failed to generate dungeon: {e}")
            pygame.quit()
            raise RuntimeError(f"Dungeon generation failed: {e}") from e

        # Initializing player at first room center
        self.player_x = int(self.rooms[0].center.x)
        self.player_y = int(self.rooms[0].center.y)
            
        self.path = None
        self.path_index = 0
        self.move_timer = 0.0
        self.move_delay = 0.15  # seconds per cell for smoother movement

        self.colors = {
            "background": (10, 10, 40),
            "floor": (50, 50, 80),
            "wall": (0, 0, 0),
            "player": (255, 100, 100),
            "path": (100, 200, 255, 100),
        }

    def handle_events(self):    # Handling user input events, false if user wants to quit, true otherwise
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // self.cell_size
                grid_y = mouse_y // self.cell_size
                
                # Check if clicked position is valid and walkable
                if (0 <= grid_x < self.dungeon_width and 
                    0 <= grid_y < self.dungeon_height and 
                    self.grid[grid_y][grid_x] > 0):
                    
                    self.path = self.pathfinder.find_path(
                        self.player_x,
                        self.player_y,
                        grid_x,
                        grid_y
                    )
                    self.path_index = 0
                    self.move_timer = 0.0  # Reset timer for new path
        return True

    def update(self, delta_time):   # Update game state based on elapsed time
        # Use delta_time for smooth, controlled movement
        if self.path and self.path_index < len(self.path) - 1:
            self.move_timer += delta_time
            
            # Only move when enough time has elapsed
            if self.move_timer >= self.move_delay:
                self.move_timer -= self.move_delay  # Keep remainder for smooth timing
                self.path_index += 1
                self.player_x, self.player_y = self.path[self.path_index]
                
                # Clear path when destination reached
                if self.path_index >= len(self.path) - 1:
                    self.path = None
                    self.path_index = 0
                    self.move_timer = 0.0

    def draw(self):  # Render the current game state to the screen
        self.screen.fill(self.colors["wall"])
        
        # Draw floor tiles
        for y in range(self.dungeon_height):
            for x in range(self.dungeon_width):
                if self.grid[y][x] > 0:
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size,
                        self.cell_size
                    )
                    pygame.draw.rect(self.screen, self.colors["floor"], rect)

        # Draw path if one exists
        if self.path:
            path_surface = pygame.Surface(
                (self.screen_width, self.screen_height),
                pygame.SRCALPHA
            )
            for x, y in self.path:
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size
                )
                pygame.draw.rect(path_surface, self.colors["path"], rect)
            self.screen.blit(path_surface, (0, 0))
        
        # Draw player
        player_rect = pygame.Rect(
            self.player_x * self.cell_size,
            self.player_y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        pygame.draw.rect(self.screen, self.colors["player"], player_rect)
        
        pygame.display.flip()

    def run(self):  # Main loop to run the dungeon generator
        running = True
        while running:
            delta_time = self.clock.tick(60) / 1000.0
            running = self.handle_events()
            self.update(delta_time)
            self.draw()
        pygame.quit()
        sys.exit()