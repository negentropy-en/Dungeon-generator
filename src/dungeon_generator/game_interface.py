import sys
import random
import pygame
from .dungeon import DungeonGenerator
from .pathfinding import AStarPathfinder


class DungeonExplorer:
    def __init__(
        self,
        *,
        width=800,
        height=800,
        dungeon_width=100,
        dungeon_height=100,
        max_rooms=None,
    ):
        pygame.init()
        self.screen_width = width
        self.screen_height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Dungeon Explorer - R: Regenerate | ESC: Quit")

        self.dungeon_width = dungeon_width
        self.dungeon_height = dungeon_height
        self.cell_size = min(width // dungeon_width, height // dungeon_height)

        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)

        # Storing desired room count
        self.desired_rooms = max(3, min(100, max_rooms)) if max_rooms is not None else None

        self.move_delay = 0.15  # seconds per cell for smoother movement
        self.path = None
        self.path_index = 0
        self.move_timer = 0.0

        # Generate dungeon with error handling
        print("Generating initial dungeon...")
        try:
            self._build_dungeon()
            print(f"Dungeon generated with {len(self.rooms)} rooms.")
        except Exception as e:
            print(f"Failed to generate dungeon: {e}")
            pygame.quit()
            raise RuntimeError(f"Dungeon generation failed: {e}") from e

        # Initializing player at first room center
        self.player_x = int(self.rooms[0].center.x)
        self.player_y = int(self.rooms[0].center.y)

        self.colors = {
            "background": (10, 10, 40),
            "floor": (50, 50, 80),
            "wall": (0, 0, 0),
            "player": (255, 100, 100),
            "path": (100, 200, 255, 100),
            "hud": (220, 220, 220),
        }

    def _build_dungeon(self):
        # Pick room count (fixed or random)
        target_rooms = (
            self.desired_rooms
            if self.desired_rooms is not None
            else random.randint(3, 100)
        )

        max_attempts = 10
        for attempt in range(max_attempts):
            try:
                self.dungeon = DungeonGenerator(
                    width=self.dungeon_width,
                    height=self.dungeon_height,
                    max_rooms=target_rooms,
                    min_room_size=4,
                    max_room_size=10,
                )
                self.rooms, _, _, _, self.grid = self.dungeon.generate()

                # Ensure minimum 3 rooms for triangulation
                if len(self.rooms) < 3:
                    print(
                        f"  Attempt {attempt + 1}: Only {len(self.rooms)} rooms, retrying..."
                    )
                    continue

                self.pathfinder = AStarPathfinder(self.grid)
                return

            except Exception as e:
                print(f"  Attempt {attempt + 1} failed: {e}")
                if attempt == max_attempts - 1:
                    raise RuntimeError(
                        "Could not generate dungeon with minimum 3 rooms"
                    ) from e

    def handle_events(self):  # Handling user input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                # ESC to quit
                if event.key == pygame.K_ESCAPE:
                    print("\nQuitting dungeon explorer...")
                    return False

                # R to regenerate dungeon
                if event.key == pygame.K_r:
                    print("\n[R] Regenerating dungeon...")
                    try:
                        self._build_dungeon()
                        # Reset player to first room center
                        self.player_x = int(self.rooms[0].center.x)
                        self.player_y = int(self.rooms[0].center.y)
                        # Clear any existing path
                        self.path = None
                        self.path_index = 0
                        self.move_timer = 0.0
                        print(f"Regenerated with {len(self.rooms)} rooms.")
                    except Exception as e:
                        print(f"Failed to regenerate: {e}")
                        return False

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x = mouse_x // self.cell_size
                grid_y = mouse_y // self.cell_size

                # Check if clicked position is valid and walkable
                if (
                    0 <= grid_x < self.dungeon_width
                    and 0 <= grid_y < self.dungeon_height
                    and self.grid[grid_y][grid_x] > 0
                ):
                    self.path = self.pathfinder.find_path(
                        self.player_x, self.player_y, grid_x, grid_y
                    )
                    self.path_index = 0
                    self.move_timer = 0.0
        return True

    def update(self, delta_time):  # Update game state based on elapsed time
        # Use delta_time for smooth, controlled movement
        if self.path and self.path_index < len(self.path) - 1:
            self.move_timer += delta_time

            # Only move when enough time has elapsed
            if self.move_timer >= self.move_delay:
                self.move_timer -= self.move_delay  # Keep remainder
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
                        self.cell_size,
                    )
                    pygame.draw.rect(self.screen, self.colors["floor"], rect)

        # Draw path if one exists
        if self.path:
            path_surface = pygame.Surface(
                (self.screen_width, self.screen_height), pygame.SRCALPHA
            )
            for x, y in self.path:
                rect = pygame.Rect(
                    x * self.cell_size,
                    y * self.cell_size,
                    self.cell_size,
                    self.cell_size,
                )
                pygame.draw.rect(path_surface, self.colors["path"], rect)
            self.screen.blit(path_surface, (0, 0))

        # Draw player
        player_rect = pygame.Rect(
            self.player_x * self.cell_size,
            self.player_y * self.cell_size,
            self.cell_size,
            self.cell_size,
        )
        pygame.draw.rect(self.screen, self.colors["player"], player_rect)

        # Draw HUD (single line, clean design)
        hud_text = f"Rooms: {len(self.rooms)} | R: regenerate | ESC: quit"
        text_surf = self.font.render(hud_text, True, self.colors["hud"])
        self.screen.blit(text_surf, (10, 10))

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
        