/** The vector table (editable) and the table of every pair. */
import { esc, fmt, signClass } from "../format";
import { length } from "../math";
import { canRemove, pairAt, SIZE as S, type ExplorerState } from "../state";

export function renderVectorRows(st: ExplorerState, spinning: boolean): string {
  const dis = spinning ? " disabled" : "";
  let h = "";
  st.vecs.forEach((v, i) => {
    const n = esc(v.n);
    h += `<tr><td><input type="radio" name="first" id="f${i}" data-first="${i}"${i === st.sel[0] ? " checked" : ""}${dis} aria-label="Make ${n} the first vector"></td>`;
    h += `<td><input type="radio" name="second" id="s${i}" data-second="${i}"${i === st.sel[1] ? " checked" : ""}${dis} aria-label="Make ${n} the second vector"></td>`;
    h += `<td class="nm">${n}</td>`;
    h += `<td><input id="vx${i}" type="number" step="1" min="${-S}" max="${S}" value="${+v.x.toFixed(2)}" data-i="${i}" data-k="x" aria-label="x of ${n}"${dis}></td>`;
    h += `<td><input id="vy${i}" type="number" step="1" min="${-S}" max="${S}" value="${+v.y.toFixed(2)}" data-i="${i}" data-k="y" aria-label="y of ${n}"${dis}></td>`;
    h += `<td class="len" id="vl${i}">${fmt(length(v))}</td>`;
    h += `<td>${canRemove(st) ? `<button type="button" class="x" id="del${i}" data-del="${i}" aria-label="Remove vector ${n}"${dis}>×</button>` : ""}</td></tr>`;
  });
  return h;
}

export function renderMatrix(st: ExplorerState): string {
  const raw = st.mode === "raw";
  let h = `<tr><th></th>${st.vecs.map((v) => `<th>${esc(v.n)}</th>`).join("")}</tr>`;
  st.vecs.forEach((v, i) => {
    h += `<tr><th>${esc(v.n)}</th>`;
    st.vecs.forEach((w, j) => {
      const pr = pairAt(st, i, j);
      const val = raw ? pr.d : pr.n;
      const pct = pr.sign === 0 ? 0 : Math.round(12 + Math.abs(pr.n) * 48);
      const bg = pr.sign === 0 ? "transparent" : `color-mix(in srgb, var(--${signClass(pr.sign)}) ${pct}%, var(--panel))`;
      const on = i === st.sel[0] && j === st.sel[1];
      const diag = i === j;
      const label = esc(`${v.n} with ${w.n}: ${fmt(val)}`);
      h += `<td><button type="button" id="gm${i}-${j}" class="${on ? "sel" : ""}${diag ? " diag" : ""}" style="background:${bg}" data-i="${i}" data-j="${j}" aria-label="${label}"${diag ? ' tabindex="-1"' : ""}>${pr.ok || raw ? fmt(val) : "?"}</button></td>`;
    });
    h += `</tr>`;
  });
  return h;
}

export function matrixHint(st: ExplorerState): string {
  return st.mode === "raw"
    ? "Raw numbers grow when a vector gets longer. The corner-to-corner squares hold each length squared."
    : "Normalized numbers stay between −1 and 1, however long the vectors are.";
}
