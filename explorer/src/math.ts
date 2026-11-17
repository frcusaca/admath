/**
 * The vector math behind the explorer. Every function here is pure: no DOM,
 * no state, same answer for the same input. The thresholds are the ones the
 * original single-file page used, so the port behaves identically.
 */

export interface Vec {
  readonly x: number;
  readonly y: number;
}

/** -1, 0 or 1. */
export type Sign = -1 | 0 | 1;

/** Below this length a vector has no direction. */
export const ZERO_LENGTH = 1e-9;
/** |normalized inner product| below this counts as a right angle. */
export const RIGHT_ANGLE_TOLERANCE = 0.004;

/** ⟨p, q⟩ = p.x q.x + p.y q.y */
export function inner(p: Vec, q: Vec): number {
  return p.x * q.x + p.y * q.y;
}

/** ‖p‖ */
export function length(p: Vec): number {
  return Math.hypot(p.x, p.y);
}

/** p turned a quarter turn to the left (counterclockwise). */
export function turnLeft(p: Vec): Vec {
  return { x: -p.y, y: p.x };
}

/**
 * ⟨p turned left, q⟩. Positive when q is on the left of p.
 * (It is also the 2D cross product p.x q.y − p.y q.x.)
 */
export function leftness(p: Vec, q: Vec): number {
  return inner(turnLeft(p), q);
}

/** True when both vectors are long enough to have a direction. */
export function hasAngle(p: Vec, q: Vec): boolean {
  return length(p) > ZERO_LENGTH && length(q) > ZERO_LENGTH;
}

/** ⟨p, q⟩ / (‖p‖ ‖q‖), clamped to [−1, 1]; null when either vector has length 0. */
export function normalizedInner(p: Vec, q: Vec): number | null {
  if (!hasAngle(p, q)) return null;
  return Math.max(-1, Math.min(1, inner(p, q) / (length(p) * length(q))));
}

/**
 * The sign of the inner product: what blue (1) and orange (−1) mean.
 * Near-right angles count as 0. With a zero-length vector the raw inner product decides.
 */
export function innerSign(p: Vec, q: Vec): Sign {
  const d = inner(p, q);
  const n = normalizedInner(p, q);
  const isZero = n === null ? Math.abs(d) < ZERO_LENGTH : Math.abs(n) < RIGHT_ANGLE_TOLERANCE;
  if (isZero) return 0;
  return d > 0 ? 1 : -1;
}

/** 1 for a counterclockwise turn from p to q, −1 for clockwise, 0 when they lie on one line. */
export function turnDirection(p: Vec, q: Vec): Sign {
  if (!hasAngle(p, q)) return 0;
  const c = leftness(p, q);
  if (Math.abs(c) < 1e-6 * (1 + length(p) * length(q))) return 0;
  return c > 0 ? 1 : -1;
}

/** The signed angle from p to q in degrees, in (−180, 180]; null when either has length 0. */
export function signedAngle(p: Vec, q: Vec): number | null {
  if (!hasAngle(p, q)) return null;
  return (Math.atan2(leftness(p, q), inner(p, q)) * 180) / Math.PI;
}

/** Everything the views need about an ordered pair (p is first, q is second). */
export interface PairFacts {
  readonly p: Vec;
  readonly q: Vec;
  /** ⟨p, q⟩ */
  readonly d: number;
  readonly lp: number;
  readonly lq: number;
  /** both vectors have a direction */
  readonly ok: boolean;
  /** normalized inner product, 0 when !ok */
  readonly n: number;
  readonly sign: Sign;
  /** ⟨p turned left, q⟩ */
  readonly cross: number;
  readonly turn: Sign;
  /** signed angle in degrees, null when !ok */
  readonly sdeg: number | null;
}

export function pairFacts(p: Vec, q: Vec): PairFacts {
  const n = normalizedInner(p, q);
  return {
    p,
    q,
    d: inner(p, q),
    lp: length(p),
    lq: length(q),
    ok: n !== null,
    n: n ?? 0,
    sign: innerSign(p, q),
    cross: leftness(p, q),
    turn: turnDirection(p, q),
    sdeg: signedAngle(p, q),
  };
}
