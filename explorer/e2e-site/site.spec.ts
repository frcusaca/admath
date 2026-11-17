// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
import { existsSync, readdirSync, readFileSync } from "node:fs";
import { join, resolve } from "node:path";
import { expect, test } from "@playwright/test";

const site = resolve(import.meta.dirname, "../../_site");

function htmlFiles(dir: string): string[] {
  return readdirSync(dir, { withFileTypes: true }).flatMap((e) =>
    e.isDirectory() ? htmlFiles(join(dir, e.name)) : e.name.endsWith(".html") ? [join(dir, e.name)] : [],
  );
}

test("no teacher guide is published with the student site", () => {
  const files = htmlFiles(site).map((f) => f.slice(site.length));
  expect(files.some((f) => /teacher/i.test(f))).toBe(false);
  expect(existsSync(join(site, "notebooks/00_teacher_guide.pdf"))).toBe(false);
});

test("the explorer mounts where explore_angles is called", async ({ page }) => {
  const errors: string[] = [];
  page.on("pageerror", (e) => errors.push(e.message));
  await page.goto("/angle-explorer.html");
  const ex = page.locator(".vecdraw-angle-explorer");
  await expect(ex.locator("#read .eq")).toContainText("⟨a, b⟩ = (4)(3) + (0)(3) = 12");
  await expect(ex.locator("#vt tbody tr")).toHaveCount(5);
  expect(errors).toEqual([]);
});

test("math is typeset with KaTeX and none of it fails", async ({ page }) => {
  await page.goto("/notebooks/00_vectors_and_inner_product.html");
  await expect(page.locator(".katex").first()).toBeVisible();
  expect(await page.locator(".katex").count()).toBeGreaterThan(100);
  expect(await page.locator(".katex-error").count()).toBe(0);
});

test("every notebook page links its PDF", async ({ page }) => {
  for (const name of ["00_vectors_and_inner_product", "04_basis_and_dimension"]) {
    await page.goto(`/notebooks/${name}.html`);
    const pdf = page.locator(`a[href$="${name}.pdf"]`).first();
    await expect(pdf).toHaveCount(1);
    expect((await page.request.get(`/notebooks/${name}.pdf`)).status()).toBe(200);
  }
});

test("the teacher site holds the guides, with the answer key checked", () => {
  const teacher = resolve(import.meta.dirname, "../../_site-teacher");
  const files = htmlFiles(teacher).map((f) => f.slice(teacher.length));
  expect(files).toContain("/notebooks/00_teacher_guide.html");
  expect(files.some((f) => /00_vectors_and_inner_product/.test(f))).toBe(false);
  const guide = readFileSync(join(teacher, "notebooks/00_teacher_guide.html"), "utf-8");
  expect(guide).toMatch(/All \d+ checks passed\./);
});
