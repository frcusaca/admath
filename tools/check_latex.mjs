// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
// Check that every $...$ and $$...$$ in notebook markdown parses with KaTeX.
//
//   node tools/check_latex.mjs notebooks/*.ipynb               check only
//   node tools/check_latex.mjs --html out/ notebooks/*.ipynb   also write an HTML preview per notebook
//
// Also catches a stray $ that is not part of any math, and a | inside inline math
// in a Markdown table row (it would split the table cell).
// Also rejects the raised dot and the times cross (\\cdot, \\times, ·, ×) in
// math and text: this course writes products as (3)(4), 2a or 2(3, 4), because
// both symbols get new meanings later (dot and cross products). See AGENTS.md.
// Exit status 1 if anything is wrong.
//
// Ported from the original tools/check_latex.js; the checks are the same, and
// the HTML previews are now opt-in instead of always written to the current folder.
import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { createRequire } from "node:module";
import { basename, join } from "node:path";
import katex from "katex";
import MarkdownIt from "markdown-it";

const require = createRequire(import.meta.url);
const md = new MarkdownIt({ html: false });

const args = process.argv.slice(2);
let htmlDir = null;
const htmlAt = args.indexOf("--html");
if (htmlAt >= 0) {
  htmlDir = args[htmlAt + 1];
  args.splice(htmlAt, 2);
  mkdirSync(htmlDir, { recursive: true });
}
if (args.length === 0) {
  console.error("usage: node tools/check_latex.mjs [--html DIR] NOTEBOOK.ipynb...");
  process.exit(2);
}

let total = 0;
let bad = 0;
const NO_PRODUCT_SIGNS = /\\(cdot|times|cdotp|ast)(?![A-Za-z])|[×·∙⋅]/;
const escapeHtml = (s) => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

for (const f of args) {
  const nb = JSON.parse(readFileSync(f, "utf8"));
  let html = "";
  for (const c of nb.cells) {
    const src = Array.isArray(c.source) ? c.source.join("") : c.source;
    if (c.cell_type === "code") {
      html += '<pre class="code">' + escapeHtml(src) + "</pre>";
      continue;
    }
    if (c.cell_type !== "markdown") continue;
    // pull out math, keep code spans intact
    const store = [];
    const hold = (k, v) => {
      store.push({ k, v });
      return "\u0000" + (store.length - 1) + "\u0000";
    };
    let t = src.replace(/(`+)([\s\S]*?)\1/g, (m) => hold("code", m));
    t = t.replace(/\$\$([\s\S]+?)\$\$/g, (m, x) => hold("disp", x));
    t = t.replace(/\$([^$\n]+?)\$/g, (m, x) => hold("inl", x));
    if (/\$/.test(t)) {
      bad++;
      const at = t.indexOf("$");
      console.log("STRAY $ in", f, ":", t.slice(Math.max(0, at - 40), at + 40).replace(/\n/g, " "));
    }
    // no dot or cross for multiplication, in math or in text (code spans are fine)
    for (const piece of [t, ...store.filter((s) => s.k !== "code").map((s) => s.v)]) {
      const hit = piece.match(NO_PRODUCT_SIGNS);
      if (hit) {
        bad++;
        console.log("PRODUCT SIGN in", f, ":", JSON.stringify(hit[0]), "in", piece.slice(Math.max(0, hit.index - 40), hit.index + 30).replace(/\n/g, " "));
      }
    }
    // pipes inside inline math within a table row would break the table
    for (const line of src.split("\n")) {
      if (!line.trim().startsWith("|")) continue;
      for (const m of line.match(/\$[^$]+\$/g) || []) {
        if (m.includes("|")) {
          bad++;
          console.log("PIPE in table math in", f, ":", m);
        }
      }
    }
    t = t.replace(/\u0000(\d+)\u0000/g, (m, i) => (store[+i].k === "code" ? store[+i].v : "MATHPH" + i + "X"));
    let h = md.render(t);
    h = h.replace(/MATHPH(\d+)X/g, (m, i) => {
      const s = store[+i];
      total++;
      try {
        return katex.renderToString(s.v, { displayMode: s.k === "disp", throwOnError: true, strict: "error" });
      } catch (e) {
        bad++;
        console.log("KATEX ERROR in", f, ":", s.v, "=>", e.message);
        return '<b style="color:red">' + escapeHtml(s.v) + "</b>";
      }
    });
    html += '<div class="md">' + h + "</div>";
  }
  if (htmlDir) {
    const katexDist = join(require.resolve("katex/package.json"), "..", "dist");
    const css = readFileSync(join(katexDist, "katex.min.css"), "utf8").replace(/url\(fonts\//g, `url(file://${katexDist}/fonts/`);
    const out = join(htmlDir, basename(f).replace(".ipynb", ".html"));
    writeFileSync(
      out,
      `<!doctype html><meta charset="utf-8"><style>${css}
  body{font:16px/1.5 system-ui,sans-serif;max-width:860px;margin:20px auto;padding:0 16px}
  table{border-collapse:collapse;margin:10px 0}td,th{border:1px solid #bbb;padding:4px 10px;text-align:left}
  pre.code{background:#f3f3f3;padding:8px 10px;border-radius:4px;font-size:13px;overflow:auto}code{background:#f3f3f3;padding:1px 4px;border-radius:3px}</style>${html}`,
    );
  }
}
console.log(`latex: ${total} math snippets in ${args.length} notebooks, ${bad} problems`);
process.exit(bad ? 1 : 0);
