/** The readout panel: the worked inner product, the chips, the numbers, and the −1…1 meter. */
import { esc, fmt, fmtSignedDegrees, signClass } from "../format";
import type { PairFacts, Sign } from "../math";

const SIGN_WORDS: Record<Sign, [string, string, string]> = {
  1: ["+", "positive", "less than 90°"],
  0: ["0", "zero", "exactly 90°"],
  [-1]: ["−", "negative", "more than 90°"],
};

function turnWords(turn: Sign, a: string, b: string): [string, string] {
  if (turn === 1) return ["↺", `counterclockwise: ${b} is on the left of ${a}`];
  if (turn === -1) return ["↻", `clockwise: ${b} is on the right of ${a}`];
  return ["↔", `no turn: ${a} and ${b} lie along one line`];
}

/** `pr` is the picked pair; `a` and `b` are the names of its first and second vector. */
export function renderReadout(pr: PairFacts, firstName: string, secondName: string): string {
  const a = esc(firstName);
  const b = esc(secondName);
  const words = SIGN_WORDS[pr.sign];
  let h = `<div style="display:flex;flex-direction:column;gap:12px">`;
  h += `<div class="eq">⟨${a}, ${b}⟩ = (${fmt(pr.p.x)})(${fmt(pr.q.x)}) + (${fmt(pr.p.y)})(${fmt(pr.q.y)}) = <b>${fmt(pr.d)}</b></div>`;
  if (pr.ok && pr.sdeg !== null) {
    const turns = turnWords(pr.turn, a, b);
    h += `<div class="chips"><div class="chip ${signClass(pr.sign)}"><i>${words[0]}</i>${words[1]}, so the angle is ${words[2]}</div>`;
    h += `<div class="chip"><i>${turns[0]}</i>${turns[1]}</div></div>`;
    h += `<dl><dt>length of ${a}</dt><dd>‖${a}‖ = ${fmt(pr.lp)}</dd><dt>length of ${b}</dt><dd>‖${b}‖ = ${fmt(pr.lq)}</dd>`;
    h += `<dt>normalized</dt><dd>${fmt(pr.d)} ÷ (${fmt(pr.lp)} × ${fmt(pr.lq)}) = <b>${fmt(pr.n)}</b></dd>`;
    h += `<dt>angle from ${a} to ${b}</dt><dd><b>${fmtSignedDegrees(pr.sdeg, pr.turn)}</b></dd>`;
    h += `<dt>left or right?</dt><dd>⟨(${fmt(-pr.p.y)}, ${fmt(pr.p.x)}), ${b}⟩ = ${fmt(pr.cross)}</dd></dl>`;
    h += `<p class="hint">(${fmt(-pr.p.y)}, ${fmt(pr.p.x)}) is ${a} turned a quarter turn to the left. A positive answer means ${b} is on that side.</p>`;
  } else {
    h += `<div class="chip"><i>?</i>a vector of length 0 has no direction, so there is no angle</div>`;
  }
  return h + `</div>`;
}

const mx = (n: number) => 150 + n * 132;

export function renderMeter(pr: PairFacts): string {
  let m = `<line class="track" x1="${mx(-1)}" y1="24" x2="${mx(1)}" y2="24"/>`;
  const ticks: [number, string, string, string][] = [
    [-1, "−1", "opposite", "start"],
    [0, "0", "perpendicular", "middle"],
    [1, "1", "same way", "end"],
  ];
  for (const [n, num, word, anchor] of ticks) {
    m += `<line class="tk" x1="${mx(n)}" y1="17" x2="${mx(n)}" y2="31"/><text x="${mx(n)}" y="10" text-anchor="middle">${num}</text><text x="${mx(n)}" y="48" text-anchor="${anchor}">${word}</text>`;
  }
  if (pr.ok) m += `<circle class="mark ${signClass(pr.sign)}" cx="${mx(pr.n)}" cy="24" r="8"/>`;
  return m;
}
