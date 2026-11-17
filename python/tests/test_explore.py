# Copyright © 2026-present CAehi.us
import base64
import json
import re

import numpy as np
import pytest

from vecdraw.explore import AngleExplorer, explore_angles


def test_defaults_name_vectors_a_b_c():
    ex = AngleExplorer(np.array([4, 0]), np.array([3, 3]), [0, 5])
    assert ex.names == ["a", "b", "c"]
    assert ex.vectors == [[4, 0], [3, 3], [0, 5]]


def test_whole_numbers_stay_whole_and_decimals_stay():
    ex = AngleExplorer([4.0, 0.0], [2.5, -1.25])
    assert ex.vectors == [[4, 0], [2.5, -1.25]]
    assert isinstance(ex.vectors[0][0], int)


def test_matrix_rows_are_vectors():
    M = np.array([[1, 2], [3, 4], [5, 6]])
    ex = AngleExplorer(M, names=["p", "q", "r"])
    assert ex.vectors == [[1, 2], [3, 4], [5, 6]]


def test_names_string_is_split_into_letters():
    assert AngleExplorer([1, 0], [0, 1], names="uv").names == ["u", "v"]


@pytest.mark.parametrize(
    "args, kwargs, message",
    [
        (([1, 2],), {}, "at least 2"),
        (([1, 2, 3], [1, 0]), {}, "2 numbers"),
        (([9, 0], [1, 0]), {}, "does not fit"),
        (([1, 0], [float("nan"), 0]), {}, "not finite"),
        (([1, 0], [0, 1]), {"names": ["a"]}, "2 vectors but 1 names"),
        (([1, 0], [0, 1]), {"names": ["a", "a"]}, "own name"),
        (([1, 0], [0, 1]), {"names": ["a", "much-too-long"]}, "characters"),
        (tuple([[1, 0]] * 9), {}, "at most 8"),
    ],
)
def test_friendly_errors(args, kwargs, message):
    with pytest.raises(ValueError, match=message):
        AngleExplorer(*args, **kwargs)


def test_mimebundle_has_html_png_and_text():
    bundle = AngleExplorer([4, 0], [3, 3])._repr_mimebundle_()
    assert set(bundle) == {"text/plain", "text/html", "image/png"}
    png = base64.b64decode(bundle["image/png"])
    assert png.startswith(b"\x89PNG")


def test_mimebundle_respects_include():
    bundle = AngleExplorer([4, 0], [3, 3])._repr_mimebundle_(include=["image/png"])
    assert set(bundle) == {"text/plain", "image/png"}


def test_html_mounts_with_the_callers_vectors():
    html = AngleExplorer([4, 0], [-2, 3], names=["u", "w"]).html()
    match = re.search(r'id="(vecdraw-angle-explorer-[0-9a-f]+)"', html)
    assert match
    call = re.search(r"mountAngleExplorer\(document\.getElementById\(\"(.+?)\"\), (\{.*\})\);", html)
    assert call and call.group(1) == match.group(1)
    assert json.loads(call.group(2)) == {"vectors": [[4, 0], [-2, 3]], "names": ["u", "w"]}


def test_html_cannot_break_out_of_the_script_tag():
    html = AngleExplorer([1, 0], [0, 1], names=["<b>", "</s"]).html()
    body = html.split("<script>", 1)[1].rsplit("</script>", 1)[0]
    assert "</script" not in body.lower()
    options = body.rsplit("mountAngleExplorer(", 1)[1]
    assert "<b>" not in options and "</s" not in options
    assert json.loads(re.search(r"(\{.*\})\);", options).group(1))["names"] == ["<b>", "</s"]


def test_a_script_end_tag_inside_the_bundle_is_neutralised(monkeypatch):
    from vecdraw import explore

    class FakeFile:
        def joinpath(self, _):
            return self

        def read_text(self, _):
            return 'var s = "</script><script>alert(1)</SCRIPT>";'

    monkeypatch.setattr(explore.resources, "files", lambda _: FakeFile())
    script = explore._explorer_script()
    assert "</script" not in script.lower()
    assert script.count("<\\/") == 2


def test_each_call_gets_its_own_element():
    a = AngleExplorer([1, 0], [0, 1]).html()
    b = AngleExplorer([1, 0], [0, 1]).html()
    assert re.search(r'id="([^"]+)"', a).group(1) != re.search(r'id="([^"]+)"', b).group(1)


def test_explore_angles_displays_and_returns_none(monkeypatch):
    shown = []
    import IPython.display

    monkeypatch.setattr(IPython.display, "display", lambda obj: shown.append(obj))
    assert explore_angles([4, 0], [3, 3]) is None
    assert len(shown) == 1 and isinstance(shown[0], AngleExplorer)


def test_static_picture_handles_a_zero_vector():
    png = AngleExplorer([0, 0], [3, 3]).figure_png()
    assert png.startswith(b"\x89PNG")
