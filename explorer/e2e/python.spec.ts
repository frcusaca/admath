// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/** The HTML that explore_angles() puts in a notebook output really runs. */
import { expect, test } from "@playwright/test";
import { pythonHtml, tempPage } from "./helpers";

test("explore_angles HTML mounts with the caller's vectors and names", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  const html = pythonHtml("AngleExplorer([1, 2], [3, -1], [-4, 0.5], names=['u', 'w', '<x>'])");
  await page.goto(tempPage(`<!doctype html><meta charset="utf-8"><body>${html}</body>`));
  const ex = page.locator(".vecdraw-angle-explorer");
  await expect(ex.locator("#read .eq")).toContainText("⟨u, w⟩ = (1)(3) + (2)(−1) = 1");
  await expect(ex.locator("#vt tbody tr")).toHaveCount(3);
  await expect(ex.locator("#vt td.nm").nth(2)).toHaveText("<x>");
  expect(errors).toEqual([]);
});

test("two explore_angles outputs on one page do not interfere", async ({ page }) => {
  const a = pythonHtml("AngleExplorer([1, 0], [0, 1])");
  const b = pythonHtml("AngleExplorer([2, 2], [-2, 2], names='pq')");
  await page.goto(tempPage(`<!doctype html><meta charset="utf-8"><body>${a}${b}</body>`));
  const all = page.locator(".vecdraw-angle-explorer");
  await expect(all).toHaveCount(2);
  await expect(all.nth(0).locator("#read .eq")).toContainText("⟨a, b⟩");
  await expect(all.nth(1).locator("#read .eq")).toContainText("⟨p, q⟩");
});

test("a frontend that inserts the output with innerHTML and re-creates scripts (JupyterLab style) still works", async ({ page }) => {
  const html = pythonHtml("AngleExplorer([3, 4], [4, -3])");
  await page.goto(tempPage(`<!doctype html><meta charset="utf-8"><body><div id="out"></div></body>`));
  await page.evaluate((h) => {
    const out = document.getElementById("out")!;
    out.innerHTML = h;
    for (const old of Array.from(out.querySelectorAll("script"))) {
      const s = document.createElement("script");
      s.textContent = old.textContent;
      old.replaceWith(s);
    }
  }, html);
  await expect(page.locator(".vecdraw-angle-explorer #read")).toContainText("exactly 90°");
});
