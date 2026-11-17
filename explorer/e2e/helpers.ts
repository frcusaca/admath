// Copyright © 2026-present CAehi.us
import { execFileSync } from "node:child_process";
import { existsSync, mkdtempSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";
import type { Locator, Page } from "@playwright/test";

const here = dirname(fileURLToPath(import.meta.url));
export const explorerDir = resolve(here, "..");
export const repoDir = resolve(explorerDir, "..");

export const ORIGINAL = pathToFileURL(join(explorerDir, "reference/angle-explorer.original.html")).href;
export const STANDALONE = pathToFileURL(join(explorerDir, "dist/standalone/angle-explorer.html")).href;
export const LIBRARY = join(explorerDir, "dist/lib/angle-explorer.js");

/** A locator inside the (open) shadow root of the explorer on a standalone page. Playwright pierces open shadow roots. */
export function q(page: Page, selector: string): Locator {
  return page.locator(selector);
}

/** Write a throwaway HTML page and return its file:// URL. */
export function tempPage(html: string): string {
  const dir = mkdtempSync(join(tmpdir(), "angle-explorer-"));
  const file = join(dir, "page.html");
  writeFileSync(file, html);
  return pathToFileURL(file).href;
}

/** HTML from the Python side: vecdraw.explore.AngleExplorer(...).html() */
export function pythonHtml(code: string): string {
  const py = [join(repoDir, ".venv/bin/python"), join(repoDir, ".venv/Scripts/python.exe")].find((p) => existsSync(p));
  if (!py) throw new Error("No .venv found; run `make setup` first.");
  return execFileSync(py, ["-c", `from vecdraw.explore import AngleExplorer\nprint(${code}.html())`], {
    encoding: "utf-8",
  });
}
