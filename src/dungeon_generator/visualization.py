import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def visualize_dungeon(rooms, corridors, triangulation=None, width=100, height=100):
    fig, ax = plt.subplots(figsize=(12, 12))
    ax.set_facecolor("black")

    # Plot Delaunay triangulation (optional)
    if triangulation:
        for t in triangulation.triangles:
            v = t.vertices
            pts = [(v[0].x, v[0].y), (v[1].x, v[1].y), (v[2].x, v[2].y), (v[0].x, v[0].y)]
            ax.plot(*zip(*pts), color="blue", linestyle=":", alpha=0.4)

    # Plot corridors
    for corridor in corridors:
        for i in range(len(corridor) - 1):
            x1, y1 = corridor[i]
            x2, y2 = corridor[i + 1]
            ax.plot([x1, x2], [y1, y2], color="gray", linewidth=2)

    # Plot rooms
    for room in rooms:
        ax.add_patch(Rectangle((room.x, room.y), room.width, room.height,
                               fill=True, color="darkslateblue", edgecolor="black", alpha=0.9))
        ax.text(room.center.x, room.center.y, str(room.id), color='white',
                ha='center', va='center', fontsize=8)

    ax.set_xlim(0, width)
    ax.set_ylim(0, height)
    ax.set_aspect("equal")
    ax.set_title("Procedural Dungeon (Delaunay + MST)")
    plt.savefig("dungeon.png", dpi=150, bbox_inches="tight")
    print("Dungeon map saved to dungeon.png")
    plt.show()