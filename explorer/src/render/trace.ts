// Copyright © 2026-present CAehi.us
/** The curve of the normalized inner product against the signed angle (drawn by Spin). */
import { esc, fmt, fmtSignedDegrees, signClass } from "../format";
import { RIGHT_ANGLE_TOLERANCE, type PairFacts } from "../math";

/** One point on the curve: s is the signed angle in degrees, n the normalized inner product. */
export interface TracePoint {
  s: number;
  n: number;
}

export const TRACE_VIEW_WIDTH = 300;
const TX0 = 30;
const TX1 = 292;
const TYT = 10;
const TYB = 98;
const tX = (d: number) => TX0 + ((d + 180) / 360) * (TX1 - TX0);
const tY = (n: number) => (TYT + TYB) / 2 - (n * (TYB - TYT)) / 2;
const dotClass = (n: number) => signClass(Math.abs(n) < RIGHT_ANGLE_TOLERANCE ? 0 : n);

export function renderTrace(pr: PairFacts, a: string, b: string, trace: readonly TracePoint[], hover: TracePoint | null): string {
  const an = esc(a);
  const bn = esc(b);
  let t = `<rect class="frame" x="${TX0}" y="${TYT - 4}" width="${TX1 - TX0}" height="${TYB - TYT + 8}" rx="3"/>`;
  for (const d of [-90, 0, 90]) t += `<line class="vg" x1="${tX(d)}" y1="${TYT - 4}" x2="${tX(d)}" y2="${TYB + 4}"/>`;
  t += `<line class="zero" x1="${TX0}" y1="${tY(0)}" x2="${TX1}" y2="${tY(0)}"/>`;
  for (const n of [1, 0, -1]) t += `<text x="${TX0 - 6}" y="${tY(n) + 4}" text-anchor="end">${fmt(n)}</text>`;
  for (const d of [-180, -90, 0, 90, 180]) {
    const anchor = d === -180 ? "start" : d === 180 ? "end" : "middle";
    t += `<text x="${tX(d)}" y="${TYB + 17}" text-anchor="${anchor}">${fmt(d)}°</text>`;
  }
  t += `<text x="${(TX0 + TX1) / 2}" y="${TYB + 31}" text-anchor="middle">angle from ${an} to ${bn} (minus is clockwise)</text>`;
  for (const p of trace) t += `<circle class="dot ${dotClass(p.n)}" cx="${tX(p.s)}" cy="${tY(p.n)}" r="2"/>`;
  if (hover) {
    t += `<line class="guide" x1="${tX(hover.s)}" y1="${TYT - 4}" x2="${tX(hover.s)}" y2="${TYB + 4}"/><circle class="dot ${dotClass(hover.n)}" cx="${tX(hover.s)}" cy="${tY(hover.n)}" r="5"/>`;
  }
  if (pr.ok && pr.sdeg !== null) t += `<circle class="now" cx="${tX(pr.sdeg)}" cy="${tY(pr.n)}" r="5"/>`;
  return t;
}

/** The sentence under the curve. Plain text (set with textContent). */
export function traceTip(a: string, b: string, trace: readonly TracePoint[], hover: TracePoint | null): string {
  if (hover) {
    const s = Math.abs(hover.n) < RIGHT_ANGLE_TOLERANCE ? 0 : Math.sign(hover.n);
    const w =
      s > 0
        ? "Positive, so the angle is less than 90°."
        : s < 0
          ? "Negative, so the angle is more than 90°."
          : "Zero, so the angle is exactly 90°.";
    const noTurn = Math.abs(hover.s) < 0.05 || Math.abs(hover.s) > 179.95;
    return `At ${fmtSignedDegrees(hover.s, noTurn ? 0 : 1)} the normalized inner product is ${fmt(hover.n)}. ${w}`;
  }
  if (trace.length) return "Hover over the curve, or tap it, to read any point. The ring is where the two vectors are now.";
  return `The ring is where ${a} and ${b} are now. Press the Spin button to draw the whole curve.`;
}

/** The traced point nearest the pointer (within 6°), or null. */
export function nearestTracePoint(
  trace: readonly TracePoint[],
  clientX: number,
  box: { left: number; width: number },
): TracePoint | null {
  const deg = ((((clientX - box.left) / box.width) * TRACE_VIEW_WIDTH - TX0) / (TX1 - TX0)) * 360 - 180;
  let best: TracePoint | null = null;
  let bd = 6;
  for (const p of trace) {
    const d = Math.abs(p.s - deg);
    if (d < bd) {
      bd = d;
      best = p;
    }
  }
  return best;
}
