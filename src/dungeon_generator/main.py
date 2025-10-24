import argparse
import random
from .dungeon import DungeonGenerator
from .visualization import visualize_dungeon


def generate_and_visualize(seed, rooms=None):  # Generating and visualizing
    if seed is not None:
        random.seed(seed)
        print(f"Using seed: {seed}")

    # Choosing a random room count in the range of 3-100 if not provided
    if rooms is None:
        rooms = random.randint(3, 100)
    else:
        rooms = max(3, min(100, rooms))

    print(f"Generating dungeon with target of {rooms} rooms...")

    max_attempts = 10
    for attempt in range(max_attempts):
        try:
            generator = DungeonGenerator(
                width=100,
                height=100,
                max_rooms=rooms,
                min_room_size=4,
                max_room_size=10,
            )
            rooms_list, corridors, _, triangulation, _ = generator.generate()

            # Ensure minimum 3 rooms for triangulation
            if len(rooms_list) < 3:
                print(
                    f"  Attempt {attempt + 1}: Only {len(rooms_list)} rooms, retrying..."
                )
                continue

            print(f"Generated {len(rooms_list)} rooms (target: {rooms}).")
            visualize_dungeon(
                rooms_list,
                corridors,
                triangulation,
                width=generator.width,
                height=generator.height,
            )
            return

        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt == max_attempts - 1:
                print("Failed to generate valid dungeon after maximum attempts.")
                print("Try a different seed or adjusting parameters.")


def run_game(rooms=None):
    try:
        from .game_interface import DungeonExplorer

        print("\n" + "=" * 60)
        print("Starting Dungeon Explorer")
        print("=" * 60)
        print("Controls:")
        print("  • Click anywhere in the rooms to move player")
        print("  • Press R to regenerate dungeon")
        print("  • Press ESC to quit")
        if rooms:
            print(f"  • Fixed room count: {rooms}")
        else:
            print("  • Random room count: 3-100 per generation")
        print("=" * 60 + "\n")

        explorer = DungeonExplorer(max_rooms=rooms)
        explorer.run()
    except ImportError as e:
        print(
            "Pygame is not installed. "
            "Please run 'poetry install --extras viewer' to install it."
        )
        print(f"Error: {e}")
    except Exception as e:
        print(f"An error occurred while running the game: {e}")


def main():
    parser = argparse.ArgumentParser(
        description="Procedural Dungeon Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --game                    # Random 3-100 rooms each regeneration
  %(prog)s --game --rooms 30         # Always 30 rooms
  %(prog)s --generate                # Random 3-100 rooms
  %(prog)s --generate --rooms 50     # Exactly 50 rooms
  %(prog)s --generate --seed 42      # Reproducible with seed
  %(prog)s --generate --rooms 25 --seed 42  # Both fixed
        """,
    )
    parser.add_argument(
        "--game", action="store_true", help="Run the interactive Pygame viewer"
    )
    parser.add_argument(
        "--generate",
        action="store_true",
        help="Generate and save a dungeon map as a PNG",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="Seed for the random number generator for reproducible dungeons",
    )
    parser.add_argument(
        "--rooms",
        type=int,
        help="Number of rooms to generate (3-100). If omitted, a random count is chosen.",
    )

    args = parser.parse_args()

    if not any([args.game, args.generate]):
        parser.print_help()
        print("\nNo action specified. Defaulting to --generate.")
        args.generate = True

    # Validate rooms if provided
    rooms = args.rooms
    if rooms is not None:
        if rooms < 3 or rooms > 100:
            print("Warning: --rooms must be between 3 and 100.")
        rooms = max(3, min(100, rooms))

    if args.game:
        run_game(rooms)
    elif args.generate:
        generate_and_visualize(args.seed, rooms)


if __name__ == "__main__":
    main()
    