// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/** The explorer's fixed markup. The dynamic parts are filled in by the render modules. */
import { esc } from "../format";

export interface TemplateOptions {
  /** Use a <main> landmark (standalone page) instead of a labelled region (embedded). */
  landmark: boolean;
  /** Show the title and the one-line introduction. */
  header: boolean;
  /** Small print at the bottom (escaped), or null for none. */
  footer: string | null;
}

export function template(opts: TemplateOptions): string {
  const open = opts.landmark ? `<main class="main">` : `<div class="main" role="region" aria-label="Angle Explorer">`;
  const close = opts.landmark ? `</main>` : `</div>`;
  const header = opts.header
    ? `<div class="header">
    <h1>Angle Explorer <span>&#10216;a, b&#10217;</span></h1>
    <p class="lede">Pick a first vector and a second vector. Drag their tips. The plot, the numbers and the table of pairs all move together.</p>
  </div>`
    : "";
  return `${open}
  ${header}

  <section class="two">
    <div class="panel">
      <h2>Plot</h2>
      <svg id="plot" viewBox="-16 -16 552 552" role="img" aria-label="Graph paper with vectors drawn from the origin. An arc runs from the first picked vector to the second."></svg>
      <div class="row">
        <p class="hint">Tap an arrow to make it the second vector. Drag a tip to change it.</p>
        <label class="check" for="snap"><input type="checkbox" id="snap" checked> Snap to whole numbers</label>
      </div>
    </div>

    <div class="panel">
      <div class="row">
        <h2>From the first vector to the second</h2>
        <button class="btn ghost small" id="swap" type="button">Swap first and second</button>
      </div>
      <div id="read" aria-live="polite"></div>
      <svg class="meter" id="meter" viewBox="0 0 300 54" role="img" aria-label="Scale from minus one to one showing the normalized inner product"></svg>
      <div class="row">
        <h3>The normalized inner product at every angle</h3>
        <button class="btn" id="spin" type="button">Spin b once around</button>
      </div>
      <svg class="trace" id="trace" viewBox="0 0 300 130" role="img" aria-label="Chart of the normalized inner product against the angle from the first vector to the second"></svg>
      <p class="hint" id="tip"></p>
      <details>
        <summary>What is this curve?</summary>
        <p>Across is the angle from the first vector to the second. A plus sign means a counterclockwise turn and a minus sign means clockwise. Up is the normalized inner product.</p>
        <p>The curve is 1 when the two vectors point the same way, 0 at a right angle, and &minus;1 when they point opposite ways. It is the same on the left and the right, so the inner product cannot tell a left turn from a right turn.</p>
        <p>This curve has a name: the cosine. The notebook function <code>angle_between</code> runs it backwards, to turn a normalized inner product into an angle.</p>
      </details>
    </div>
  </section>

  <section class="two">
    <div class="panel">
      <div class="row">
        <h2>Vectors</h2>
        <div class="btns">
          <button class="btn ghost" id="copy" type="button">Copy as NumPy</button>
          <button class="btn ghost" id="add" type="button">Add a vector</button>
        </div>
      </div>
      <div class="scroll">
        <table id="vt">
          <thead><tr><th>1st</th><th>2nd</th><th>Name</th><th>x</th><th>y</th><th>Length</th><th></th></tr></thead>
          <tbody></tbody>
        </table>
      </div>
      <div class="copy" id="copybox" hidden>
        <label class="hint" for="code" id="copymsg">Paste this into a code cell.</label>
        <textarea id="code" rows="3" readonly spellcheck="false"></textarea>
      </div>
    </div>

    <div class="panel">
      <div class="row">
        <h2>Every pair at once</h2>
        <div class="seg" role="group" aria-label="Which inner product to show">
          <button type="button" id="mraw" aria-pressed="false">Raw</button>
          <button type="button" id="mnorm" aria-pressed="true">Normalized</button>
        </div>
      </div>
      <div class="scroll"><table id="gm"></table></div>
      <p class="legend">
        <span><span class="sw" style="background:var(--pos)"></span>positive</span>
        <span><span class="sw" style="background:var(--neg)"></span>negative</span>
        <span><span class="sw" style="border:1.5px solid var(--muted)"></span>zero</span>
      </p>
      <p class="hint">Tap a square to pick that pair. The row is the first vector and the column is the second.</p>
      <p class="hint" id="gmhint"></p>
    </div>
  </section>
${opts.footer ? `  <footer class="foot">${esc(opts.footer)}</footer>\n` : ""}${close}`;
}
