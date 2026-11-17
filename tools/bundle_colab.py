# Copyright © 2026-present CAehi.us
# SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
"""Bundle the student notebooks for Colab.

    python tools/bundle_colab.py       -> dist/colab/*.ipynb and dist/colab/admath-notebooks.zip

Only student notebooks (never teacher guides), with no outputs, and each with
its Colab title set. Kids can upload a notebook from the zip to Colab
(File > Upload notebook), or open it straight from GitHub once the repository
is public: see the links on the site's front page.
The setup cell in each notebook installs vecdraw from the repository in course.toml.
"""
import copy
import zipfile
from pathlib import Path

from nbutil import ROOT, course_config, fail, load, save, student_notebooks

OUT = ROOT / "dist" / "colab"


def main():
    repo = course_config()["repository"]
    warnings = []
    if "CHANGE-ME" in repo["url"]:
        warnings.append("course.toml still has the placeholder URL: the setup cell will stop in Colab")
    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.ipynb"):
        old.unlink()
    written = []
    for path in student_notebooks():
        nb = copy.deepcopy(load(path))
        for cell in nb["cells"]:
            if cell["cell_type"] == "code":
                cell["outputs"] = []
                cell["execution_count"] = None
        nb.setdefault("metadata", {}).setdefault("colab", {})["name"] = path.name
        nb["metadata"]["colab"]["provenance"] = []
        target = OUT / path.name
        save(target, nb)
        written.append(target)
    if not written:
        fail(["no student notebooks found"])
    archive = OUT / "admath-notebooks.zip"
    with zipfile.ZipFile(archive, "w", zipfile.ZIP_DEFLATED) as z:
        for target in written:
            z.write(target, arcname=target.name)
    print(f"colab: {len(written)} student notebooks in {archive.relative_to(ROOT)}")
    for w in warnings:
        print("WARNING:", w)


if __name__ == "__main__":
    main()
