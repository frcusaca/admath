"""
explore_angles - show the Angle Explorer in a notebook, seeded with your vectors.

Data flows one way: from Python into the explorer. To bring vectors back,
press "Copy as NumPy" in the explorer and paste the line into a code cell.

How it works: the explorer is a small JavaScript program (built from the
`explorer/` folder of the course repository and stored next to this file).
explore_angles puts that program, and your vectors, into the cell output.
Notebook pages show the interactive explorer. Outputs that cannot run
JavaScript, such as a PDF, show a plain matplotlib picture instead.
"""
import base64
import io
import json
import re
import uuid
from importlib import resources

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg

# The explorer draws graph paper from -LIMIT to +LIMIT and holds at most MAX_VECTORS.
LIMIT = 8
MAX_VECTORS = 8
MAX_NAME_LENGTH = 8
DEFAULT_NAMES = "abcdefgh"

POSITIVE = "#1c6bb0"   # the explorer's blue: inner product is positive
NEGATIVE = "#c44d1c"   # the explorer's orange: inner product is negative
INK = "#17242b"
MUTED = "#566a63"


def explore_angles(*vectors, names=None):
    """Show the Angle Explorer in this cell's output, starting with your vectors.

    explore_angles(a, b)                     two vectors, named a and b
    explore_angles(a, b, c, names=["x", "y", "z"])
    explore_angles(M)                        every row of the matrix M is a vector

    Each vector has 2 numbers, each between -8 and 8. You can give 2 to 8 vectors.
    """
    explorer = AngleExplorer(*vectors, names=names)
    try:
        from IPython.display import display
    except ImportError:
        explorer.figure_png()   # check that drawing works, then say where to look
        print("explore_angles needs a notebook (Jupyter or Colab) to show the explorer.")
        return None
    display(explorer)
    return None


class AngleExplorer:
    """The value explore_angles displays. Notebooks ask it for HTML, PDFs for a PNG."""

    def __init__(self, *vectors, names=None):
        self.vectors = _clean_vectors(vectors)
        self.names = _clean_names(names, len(self.vectors))

    def options(self):
        """The starting state handed to the explorer's mountAngleExplorer()."""
        return {
            "vectors": self.vectors,
            "names": self.names,
        }

    def __repr__(self):
        pairs = ", ".join(n + "=" + str(v) for n, v in zip(self.names, self.vectors))
        return "AngleExplorer(" + pairs + ")"

    def _repr_mimebundle_(self, include=None, exclude=None):
        bundle = {"text/plain": repr(self)}
        if _wanted("image/png", include, exclude):
            bundle["image/png"] = base64.b64encode(self.figure_png()).decode("ascii")
        if _wanted("text/html", include, exclude):
            html = self.html()
            if html is not None:
                bundle["text/html"] = html
        return bundle

    def html(self):
        """A <div> plus a <script> that mounts the explorer into it."""
        script = _explorer_script()
        if script is None:
            return None
        element_id = "vecdraw-angle-explorer-" + uuid.uuid4().hex[:12]
        options = _json_for_script(self.options())
        return (
            '<div id="' + element_id + '" class="vecdraw-angle-explorer"></div>\n'
            "<script>\n"
            + script
            + "\n;AngleExplorer.mountAngleExplorer(document.getElementById(\""
            + element_id
            + "\"), "
            + options
            + ");\n</script>"
        )

    def figure_png(self):
        """A still picture of the vectors, with the angle from the first to the second."""
        fig = Figure(figsize=(5, 5), dpi=110)
        FigureCanvasAgg(fig)
        ax = fig.add_subplot()
        _draw_static(ax, self.vectors, self.names)
        buffer = io.BytesIO()
        fig.savefig(buffer, format="png", bbox_inches="tight")
        return buffer.getvalue()


def _wanted(mime, include, exclude):
    if include is not None and mime not in include:
        return False
    if exclude is not None and mime in exclude:
        return False
    return True


def _clean_vectors(vectors):
    """Turn what the caller passed into a list of [x, y] lists of plain floats."""
    if len(vectors) == 1:
        only = np.asarray(vectors[0], dtype=float)
        if only.ndim == 2:              # a matrix: each row is a vector
            vectors = list(only)
    if len(vectors) < 2:
        raise ValueError("explore_angles needs at least 2 vectors, so there is an angle to show.")
    if len(vectors) > MAX_VECTORS:
        raise ValueError(f"explore_angles can show at most {MAX_VECTORS} vectors. You gave {len(vectors)}.")
    cleaned = []
    for position, vector in enumerate(vectors, start=1):
        try:
            array = np.asarray(vector, dtype=float)
        except (TypeError, ValueError):
            raise ValueError(f"Vector number {position} is not a list of numbers: {vector!r}") from None
        if array.shape != (2,):
            raise ValueError(
                f"The Angle Explorer draws flat vectors with 2 numbers. "
                f"Vector number {position} has shape {array.shape}."
            )
        if not np.all(np.isfinite(array)):
            raise ValueError(f"Vector number {position} has a number that is not finite: {vector!r}")
        if np.any(np.abs(array) > LIMIT):
            raise ValueError(
                f"The explorer's graph paper runs from -{LIMIT} to {LIMIT}. "
                f"Vector number {position} is {array.tolist()}, which does not fit."
            )
        cleaned.append([_tidy(array[0]), _tidy(array[1])])
    return cleaned


def _tidy(number):
    """Whole numbers stay whole (4, not 4.0) so the explorer shows them simply."""
    number = float(number)
    if number.is_integer():
        return int(number)
    return round(number, 6)


def _clean_names(names, count):
    if names is None:
        return list(DEFAULT_NAMES[:count])
    if isinstance(names, str):
        names = list(names)     # explore_angles(a, b, names="pq") is allowed
    names = [str(n) for n in names]
    if len(names) != count:
        raise ValueError(f"You gave {count} vectors but {len(names)} names.")
    if len(set(names)) != len(names):
        raise ValueError(f"Each vector needs its own name. These repeat: {names}")
    for n in names:
        if n.strip() == "" or len(n) > MAX_NAME_LENGTH:
            raise ValueError(f"Names must be 1 to {MAX_NAME_LENGTH} characters long. Check {n!r}.")
    return names


def _explorer_script():
    """The built explorer program, or None if it has not been built yet."""
    try:
        text = resources.files("vecdraw").joinpath("static/angle-explorer.iife.js").read_text("utf-8")
    except FileNotFoundError:
        return None
    # A literal "</script" anywhere in the program would end the <script> tag early.
    # "<\/" means the same thing to JavaScript inside strings and regular expressions.
    return re.sub(r"</(script)", r"<\\/\1", text, flags=re.IGNORECASE)


def _json_for_script(value):
    """JSON that is safe to put inside a <script> tag."""
    text = json.dumps(value)
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def _draw_static(ax, vectors, names):
    """The PDF picture: arrows from the origin and an arc from the first vector to the second."""
    ax.set_xlim(-LIMIT - 0.5, LIMIT + 0.5)
    ax.set_ylim(-LIMIT - 0.5, LIMIT + 0.5)
    ax.set_aspect("equal")
    ax.set_xticks(range(-LIMIT, LIMIT + 1, 2))
    ax.set_yticks(range(-LIMIT, LIMIT + 1, 2))
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color=MUTED, linewidth=1)
    ax.axvline(0, color=MUTED, linewidth=1)

    first = np.array(vectors[0], dtype=float)
    second = np.array(vectors[1], dtype=float)
    inner = float(np.dot(first, second))
    lengths = float(np.linalg.norm(first) * np.linalg.norm(second))
    if lengths > 1e-9:
        normalized = inner / lengths
        # blue and orange mean only the sign of the inner product
        if abs(normalized) < 0.004:
            color = INK
        elif inner > 0:
            color = POSITIVE
        else:
            color = NEGATIVE
        cross = first[0] * second[1] - first[1] * second[0]
        start = np.arctan2(first[1], first[0])
        turn = np.arctan2(cross, inner)
        steps = np.linspace(start, start + turn, 60)
        ax.plot(1.5 * np.cos(steps), 1.5 * np.sin(steps), color=color, linewidth=2.5)
        middle = start + turn / 2
        degrees = np.degrees(turn)
        if abs(cross) < 1e-6 * (1 + lengths):
            text = f"{abs(degrees):.1f}°"
        else:
            text = f"{degrees:+.1f}°"
        ax.text(3.0 * np.cos(middle), 3.0 * np.sin(middle), text.replace("-", "−"),
                ha="center", va="center", fontsize=11, fontweight="bold", color=INK,
                bbox={"boxstyle": "round,pad=0.15", "facecolor": "white", "edgecolor": "none", "alpha": 0.85})
        ax.set_title(f"⟨{names[0]}, {names[1]}⟩ = {_number(inner)},  normalized {_number(normalized)}",
                     fontsize=11)

    for index in range(len(vectors)):
        v = vectors[index]
        picked = index < 2
        ax.annotate("", xy=(v[0], v[1]), xytext=(0, 0),
                    arrowprops={"arrowstyle": "-|>", "color": INK if picked else MUTED,
                                "linewidth": 2.5 if picked else 1.6, "mutation_scale": 16})
        length = float(np.hypot(v[0], v[1]))
        if length > 1e-9:
            spot = (v[0] + v[0] / length * 0.9, v[1] + v[1] / length * 0.9)
        else:
            spot = (0.5, 0.5)
        ax.text(spot[0], spot[1], names[index], ha="center", va="center",
                fontsize=13 if picked else 11, fontweight="bold", color=INK if picked else MUTED)


def _number(value):
    if abs(value - round(value)) < 1e-4:
        return str(int(round(value))).replace("-", "−")
    return f"{value:.2f}".replace("-", "−")
