// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/** The graph paper: grid, arrows, and the arc from the first vector to the second. */
import { esc, fmt, fmtSignedDegrees, signClass } from "../format";
import { C, U, X, Y } from "../geometry";
import { length } from "../math";
import { currentPair, SIZE as S, type ExplorerState } from "../state";

export function renderPlot(st: ExplorerState, spinning: boolean): string {
  let h = "";
  for (let k = -S; k <= S; k++) {
    const c = k === 0 ? "ax" : "gr";
    h += `<line class="${c}" x1="${X(k)}" y1="${Y(-S - 0.5)}" x2="${X(k)}" y2="${Y(S + 0.5)}"/>`;
    h += `<line class="${c}" x1="${X(-S - 0.5)}" y1="${Y(k)}" x2="${X(S + 0.5)}" y2="${Y(k)}"/>`;
    if (k !== 0 && k % 2 === 0) {
      h += `<text class="tick" x="${X(k)}" y="${Y(0) + 14}" text-anchor="middle">${fmt(k)}</text>`;
      h += `<text class="tick" x="${X(0) - 6}" y="${Y(k) + 4}" text-anchor="end">${fmt(k)}</text>`;
    }
  }
  const pr = currentPair(st);
  if (pr.ok && pr.sdeg !== null) {
    const t1 = Math.atan2(pr.p.y, pr.p.x);
    const dl = (pr.sdeg * Math.PI) / 180;
    const t2 = t1 + dl;
    const r = 1.5 * U;
    const at = (t: number, rr: number): [number, number] => [C + rr * Math.cos(t), C - rr * Math.sin(t)];
    const c = pr.sign === 0 ? "flat" : signClass(pr.sign);
    if (Math.abs(dl) > 1e-6) {
      const a = at(t1, r);
      const b = at(t2, r);
      const sweep = dl > 0 ? 0 : 1;
      if (pr.sign !== 0) h += `<path class="wedge ${c}" d="M${C} ${C} L${a[0]} ${a[1]} A${r} ${r} 0 0 ${sweep} ${b[0]} ${b[1]} Z"/>`;
      h += `<path class="arc ${c}" d="M${a[0]} ${a[1]} A${r} ${r} 0 0 ${sweep} ${b[0]} ${b[1]}"/>`;
      if (pr.turn !== 0 && Math.abs(dl) > 0.25) {
        // arrowhead: which way the turn goes
        const dir = dl > 0 ? 1 : -1;
        const tx = -Math.sin(t2) * dir;
        const ty = -Math.cos(t2) * dir;
        const nx = Math.cos(t2);
        const ny = -Math.sin(t2);
        const bx = b[0] - tx * 11;
        const by = b[1] - ty * 11;
        h += `<polygon class="${c}" points="${b[0] + tx * 2},${b[1] + ty * 2} ${bx + nx * 6},${by + ny * 6} ${bx - nx * 6},${by - ny * 6}"/>`;
      }
      if (pr.sign === 0) {
        const s = 0.75 * U;
        const p1 = at(t1, s);
        const p2 = at(t2, s);
        h += `<path class="square" d="M${p1[0]} ${p1[1]} L${p1[0] + p2[0] - C} ${p1[1] + p2[1] - C} L${p2[0]} ${p2[1]}"/>`;
      }
    }
    const m = at(t1 + dl / 2, r + 0.95 * U);
    h += `<text class="deg" x="${m[0]}" y="${m[1] + 5}" text-anchor="middle">${fmtSignedDegrees(pr.sdeg, pr.turn)}</text>`;
  }
  // unpicked arrows first, so the picked two are drawn on top
  const order = st.vecs
    .map((_, i) => i)
    .sort((a, b) => Number(st.sel.includes(a)) - Number(st.sel.includes(b)));
  for (const i of order) {
    const v = st.vecs[i];
    if (!v) continue;
    const on = st.sel.includes(i) ? " sel" : "";
    const name = esc(v.n);
    const tx = X(v.x);
    const ty = Y(v.y);
    const L = length(v) * U;
    if (L > 1e-6) {
      const ux = (v.x * U) / L;
      const uy = (-v.y * U) / L;
      const hd = on ? 15 : 11;
      const hw = on ? 7 : 5;
      const bx = tx - ux * hd;
      const by = ty - uy * hd;
      h += `<line class="arw${on}" x1="${C}" y1="${C}" x2="${bx}" y2="${by}"/>`;
      h += `<polygon class="hdp${on}" points="${tx},${ty} ${bx - uy * hw},${by + ux * hw} ${bx + uy * hw},${by - ux * hw}"/>`;
      h += `<text class="lab${on}" x="${tx + ux * 17}" y="${ty + uy * 17 + 6}" text-anchor="middle">${name}</text>`;
      if (on) {
        const cx = tx + ux * 38;
        const cy = ty + uy * 38;
        h += `<circle class="bdg" cx="${cx}" cy="${cy}" r="9"/><text class="bdt" x="${cx}" y="${cy + 4}" text-anchor="middle">${i === st.sel[0] ? 1 : 2}</text>`;
      }
    } else {
      h += `<text class="lab${on}" x="${C + 14}" y="${C - 10}">${name}</text>`;
    }
    if (on && !spinning) h += `<circle class="grab" cx="${tx}" cy="${ty}" r="13"/>`;
  }
  return h;
}
