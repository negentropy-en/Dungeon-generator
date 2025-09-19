import argparse
import random
from .dungeon import DungeonGenerator
from .visualization import visualize_dungeon

def generate_and_visualize(seed):
    if seed:
        random.seed(seed)
    print("Generating dungeon...")
    g = DungeonGenerator(width=100, height=100, max_rooms=20, min_room_size=6, max_room_size=12)
    rooms, corridors, _, triangulation, _ = g.generate()
    if rooms:
        print(f"Generated {len(rooms)} rooms.")
        visualize_dungeon(rooms, corridors, triangulation, width=g.width, height=g.height)
    else:
        print("Could not generate any rooms. Try adjusting parameters.")

def run_game():
    try:
        from .game_interface import DungeonExplorer
        explorer = DungeonExplorer()
        explorer.run()
    except ImportError:
        print("Pygame is not installed. Please run 'poetry install --with viewer' to install it.")
    except Exception as e:
        print(f"An error occurred while running the game: {e}")

def main():
    parser = argparse.ArgumentParser(description="Procedural Dungeon Generator")
    parser.add_argument("--game", action="store_true", help="Run the interactive Pygame viewer")
    parser.add_argument("--generate", action="store_true", help="Generate and save a dungeon map as a PNG")
    parser.add_argument("--seed", type=int, help="Seed for the random number generator for reproducible dungeons")
    
    args = parser.parse_args()

    if not any(vars(args).values()):
         parser.print_help()
         print("\nNo action specified. Defaulting to --generate.")
         args.generate = True

    if args.game:
        run_game()
    elif args.generate:
        generate_and_visualize(args.seed)

if __name__ == "__main__":
    main()
    
"""Needs some work and other parts as well"""