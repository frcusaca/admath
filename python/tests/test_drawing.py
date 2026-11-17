# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
import matplotlib.pyplot as plt
import numpy as np
import pytest

import vecdraw
from vecdraw import angle_between, draw_path, draw_vector, new_grid


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def test_angle_between_known_angles():
    assert angle_between([4, 0], [3, 3]) == 45.0
    assert angle_between([3, 4], [-8, 6]) == 90.0
    assert angle_between([1, 0], [-1, 0]) == 180.0


def test_draw_vector_returns_tip():
    new_grid(6)
    tip = draw_vector([3, 4], start=(1, 1), label="a")
    assert np.allclose(tip, [4, 5])


def test_draw_path_ends_at_sum():
    new_grid(8)
    end = draw_path([[1, 2], [3, -1]], labels=["a", "b"])
    assert np.allclose(end, [4, 1])


def test_colors_list_is_shared_with_star_import():
    # Deep 6 asks kids to run COLORS[0] = "black" after `from vecdraw import *`.
    # That only works because both names point at the same list.
    namespace = {}
    exec("from vecdraw import *", namespace)
    assert namespace["COLORS"] is vecdraw.COLORS


def test_star_import_still_provides_np_and_plt():
    # The old %%writefile library leaked np and plt through `import *`;
    # notebooks may rely on that, so the package keeps it.
    namespace = {}
    exec("from vecdraw import *", namespace)
    assert namespace["np"] is np
    assert namespace["plt"] is plt
    assert callable(namespace["explore_angles"])


def test_every_old_function_is_still_there():
    for name in ["new_grid", "draw_vector", "draw_path", "draw_point", "draw_dots",
                 "draw_skewed_grid", "draw_digit", "angle_between", "show", "COLORS"]:
        assert hasattr(vecdraw, name), name
