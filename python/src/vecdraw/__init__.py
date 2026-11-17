"""
vecdraw - a tiny helper for drawing vectors on graph paper.

READ ME! Nothing in here is magic. Every function is a few lines of
NumPy and matplotlib that you could have written yourself.
Change something, run the cell again, and see what happens.
"""
import numpy as np
import matplotlib.pyplot as plt

# Colors that are easy to tell apart (also for color-blind readers).
COLORS = ["#0072B2", "#D55E00", "#009E73", "#CC79A7", "#E69F00", "#56B4E9"]

_size = 6     # how far the graph paper reaches in each direction
_count = 0    # how many arrows we have drawn so far (picks the next color)


def new_grid(size=6):
    """Start a fresh sheet of graph paper that runs from -size to +size."""
    global _size, _count
    _size = size
    _count = 0
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.set_xlim(-size, size)
    ax.set_ylim(-size, size)
    ax.set_aspect("equal")                  # one step right = one step up
    if size <= 12:                          # small paper: a line at every whole number
        ax.set_xticks(range(-size, size + 1))
        ax.set_yticks(range(-size, size + 1))
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="black", linewidth=1)   # the x-axis
    ax.axvline(0, color="black", linewidth=1)   # the y-axis
    return ax


def _paper():
    """Give back the sheet we are drawing on. Make one if there is none."""
    if plt.get_fignums():
        return plt.gca()
    return new_grid(_size)


def _next_color():
    """Pick the next color from the list, starting over when we run out."""
    global _count
    color = COLORS[_count % len(COLORS)]
    _count = _count + 1
    return color


def draw_vector(v, start=(0, 0), color=None, label=None, label_at="tip"):
    """Draw the vector v as an arrow that begins at start.

    The label goes just past the tip, or beside the middle of the arrow
    if you say label_at="middle".
    Gives back the tip of the arrow (start + v), so the next arrow
    can begin where this one ended.
    """
    ax = _paper()
    v = np.array(v, dtype=float)
    start = np.array(start, dtype=float)
    if color is None:
        color = _next_color()
    ax.quiver(start[0], start[1], v[0], v[1],
              angles="xy", scale_units="xy", scale=1,   # draw at true size
              color=color, width=0.008, zorder=3)
    tip = start + v
    if label is not None:
        length = np.linalg.norm(v)
        if length == 0:
            spot = tip + np.array([0.0, _size * 0.07])
        elif label_at == "middle":
            sideways = np.array([-v[1], v[0]]) / length   # v turned a quarter turn
            spot = start + v / 2 + sideways * _size * 0.07
        else:
            spot = tip + v / length * _size * 0.07        # just past the tip
        ax.text(spot[0], spot[1], label, color=color,
                fontsize=13, fontweight="bold", ha="center", va="center")
    return tip


def draw_point(p, label=None, color="black"):
    """Draw a dot at the point p, with an optional name next to it."""
    ax = _paper()
    ax.plot(p[0], p[1], "o", color=color, markersize=8, zorder=4)
    if label is not None:
        ax.text(p[0] + _size * 0.04, p[1] + _size * 0.04, label,
                color=color, fontsize=12)


def draw_path(steps, start=(0, 0), labels=None):
    """Draw a list of vectors tip-to-tail, like a trip with several legs.

    Gives back the place where the trip ends.
    """
    place = np.array(start, dtype=float)
    for i, step in enumerate(steps):
        name = labels[i] if labels is not None else None
        place = draw_vector(step, start=place, label=name, label_at="middle")
    return place


def draw_dots(points, color="gray", size=18):
    """Draw many points at once. points is a list of [x, y] pairs."""
    ax = _paper()
    points = np.array(points, dtype=float)
    ax.scatter(points[:, 0], points[:, 1], s=size, color=color, zorder=2)


def draw_skewed_grid(b1, b2, color="#E69F00"):
    """Draw the slanted graph paper you get from the two moves b1 and b2."""
    ax = _paper()
    n = 3 * _size                           # enough lines to cover the sheet
    b1 = np.array(b1, dtype=float)
    b2 = np.array(b2, dtype=float)
    for k in range(-n, n + 1):
        # a line in the b1 direction, shifted over by k copies of b2
        begin = k * b2 - n * b1
        end = k * b2 + n * b1
        ax.plot([begin[0], end[0]], [begin[1], end[1]], color=color, linewidth=1, alpha=0.7)
        # a line in the b2 direction, shifted over by k copies of b1
        begin = k * b1 - n * b2
        end = k * b1 + n * b2
        ax.plot([begin[0], end[0]], [begin[1], end[1]], color=color, linewidth=1, alpha=0.7)


def angle_between(a, b):
    """The angle between vectors a and b, in degrees."""
    a = np.array(a, dtype=float)
    b = np.array(b, dtype=float)
    cosine = np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))
    cosine = np.clip(cosine, -1, 1)     # guard against tiny rounding errors
    degrees = np.degrees(np.arccos(cosine))
    return round(float(degrees), 2)     # two decimal places is plenty


def draw_digit(segments, color="#D55E00"):
    """Draw a calculator digit from 7 numbers: 1 lights a bar, 0 leaves it dark.

    The bars, in order: top, upper right, lower right, bottom,
    lower left, upper left, middle.
    """
    # where each bar sits: (left, bottom, width, height)
    bars = [(1, 9.2, 4, 0.8),       # top
            (5, 5.2, 0.8, 4),       # upper right
            (5, 1, 0.8, 4),         # lower right
            (1, 0.2, 4, 0.8),       # bottom
            (0.2, 1, 0.8, 4),       # lower left
            (0.2, 5.2, 0.8, 4),     # upper left
            (1, 4.7, 4, 0.8)]       # middle
    fig, ax = plt.subplots(figsize=(1.5, 2.5))
    for i in range(7):
        left, bottom, width, height = bars[i]
        shade = color if segments[i] == 1 else "#DDDDDD"    # lit or dark
        ax.add_patch(plt.Rectangle((left, bottom), width, height, color=shade))
    ax.set_xlim(0, 6)
    ax.set_ylim(0, 10.2)
    ax.set_aspect("equal")
    ax.axis("off")


def show():
    """Show the picture."""
    plt.show()
