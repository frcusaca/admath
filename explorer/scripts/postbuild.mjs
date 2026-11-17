// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
// After `vite build`: give the standalone page its real name, and copy the
// classic-script build into the Python package (python/src/vecdraw/static/),
// which is what explore_angles() embeds in notebook outputs.
import { copyFileSync, existsSync, mkdirSync, renameSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const dist = resolve(here, "../dist");
const page = resolve(dist, "standalone/index.html");
if (existsSync(page)) renameSync(page, resolve(dist, "standalone/angle-explorer.html"));

const pyStatic = resolve(here, "../../python/src/vecdraw/static");
mkdirSync(pyStatic, { recursive: true });
copyFileSync(resolve(dist, "lib/angle-explorer.iife.js"), resolve(pyStatic, "angle-explorer.iife.js"));
console.log("standalone: dist/standalone/angle-explorer.html");
console.log("python:     python/src/vecdraw/static/angle-explorer.iife.js");
