import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

# Visualization module for generating dungeon map images.


def visualize_dungeon(
    rooms, corridors, triangulation=None, width=100, height=100
):
    # rooms: List of Room objects to visualize
    # corridors: List of corridor paths (lists of coordinate tuples)
    # triangulation: Optional DelaunayTriangulation object to overlay
    # width: Dungeon width for plot bounds
    # height: Dungeon height for plot bounds

    # We only use 'ax', so 'fig' is marked as unused with '_'
    _, ax = plt.subplots(figsize=(12, 12))
    ax.set_facecolor("black")

    # Plot Delaunay triangulation
    if triangulation:
        for triangle in triangulation.triangles:
            vertices = triangle.vertices
            pts = [
                (vertices[0].x, vertices[0].y),
                (vertices[1].x, vertices[1].y),
                (vertices[2].x, vertices[2].y),
                (vertices[0].x, vertices[0].y),
            ]
            ax.plot(*zip(*pts), color="blue", linestyle=":", alpha=0.4, zorder=1)

    # Plot corridors
    for corridor in corridors:
        for i in range(len(corridor) - 1):
            x1, y1 = corridor[i]
            x2, y2 = corridor[i + 1]
            ax.plot([x1, x2], [y1, y2], color="gray", linewidth=2, zorder=2)

    # Plot rooms
    for room in rooms:
        ax.add_patch(
            Rectangle(
                (room.x, room.y),
                room.width,
                room.height,
                fill=True,
                facecolor="darkslateblue",
                edgecolor="white",
                linewidth=1,
                alpha=0.9,
                zorder=3,
            )
        )
        # Room IDs on top of everything for easy identification
        ax.text(
            room.center.x,
            room.center.y,
            str(room.id),
            color="white",
            ha="center",
            va="center",
            fontsize=8,
            zorder=4,
        )

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.set.title("Procedural Dungeon (Delaunay + MST)")
    plt.savefig("dungeon.png", dpi=150, bbox_inches="tight")
    print("Dungeon map saved to dungeon.png")
    plt.show()
    