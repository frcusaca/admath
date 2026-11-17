// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
import { describe, expect, it } from "vitest";
import {
  hasAngle,
  inner,
  innerSign,
  length,
  leftness,
  normalizedInner,
  pairFacts,
  signedAngle,
  turnDirection,
  turnLeft,
} from "./math";

const v = (x: number, y: number) => ({ x, y });

describe("inner product and length", () => {
  it("computes ⟨a, b⟩", () => {
    expect(inner(v(3, 4), v(2, 1))).toBe(10);
    expect(inner(v(1, 5), v(5, -1))).toBe(0);
    expect(inner(v(2, 1), v(-3, 1))).toBe(-5);
  });
  it("computes ‖a‖ and ‖a‖² = ⟨a, a⟩", () => {
    expect(length(v(3, 4))).toBe(5);
    expect(length(v(-5, 12))).toBe(13);
    expect(inner(v(6, 8), v(6, 8))).toBe(length(v(6, 8)) ** 2);
  });
});

describe("normalized inner product", () => {
  it("is 1, 0, −1 for same, perpendicular, opposite", () => {
    expect(normalizedInner(v(3, 4), v(6, 8))).toBeCloseTo(1);
    expect(normalizedInner(v(3, 4), v(-8, 6))).toBeCloseTo(0);
    expect(normalizedInner(v(3, 4), v(-6, -8))).toBeCloseTo(-1);
    expect(normalizedInner(v(3, 4), v(24, 7))).toBeCloseTo(0.8);
  });
  it("never leaves [−1, 1], even with rounding", () => {
    const n = normalizedInner(v(0.1, 0.2), v(0.30000000000000004, 0.6));
    expect(n).not.toBeNull();
    expect(Math.abs(n as number)).toBeLessThanOrEqual(1);
  });
  it("is null when a vector has length 0", () => {
    expect(normalizedInner(v(0, 0), v(1, 1))).toBeNull();
    expect(hasAngle(v(1, 1), v(0, 0))).toBe(false);
  });
});

describe("sign: the only thing blue and orange mean", () => {
  it("is +1, 0, −1 by the angle", () => {
    expect(innerSign(v(4, 0), v(3, 3))).toBe(1);
    expect(innerSign(v(4, 0), v(0, 5))).toBe(0);
    expect(innerSign(v(4, 0), v(-4, 2))).toBe(-1);
  });
  it("treats a near-right angle as zero", () => {
    // normalized ≈ 0.003 < 0.004
    expect(innerSign(v(1, 0), v(0.003, 1))).toBe(0);
    expect(innerSign(v(1, 0), v(0.005, 1))).toBe(1);
  });
  it("is 0 with a zero vector", () => {
    expect(innerSign(v(0, 0), v(3, 3))).toBe(0);
  });
});

describe("turn direction and signed angle", () => {
  it("turnLeft is a quarter turn counterclockwise", () => {
    expect(turnLeft(v(3, 1))).toEqual({ x: -1, y: 3 });
    expect(inner(turnLeft(v(3, 1)), v(3, 1))).toBe(0);
  });
  it("leftness is positive when b is on the left of a", () => {
    expect(leftness(v(1, 0), v(0, 1))).toBe(1);
    expect(leftness(v(1, 0), v(0, -1))).toBe(-1);
  });
  it("counterclockwise is +, clockwise is −, on one line is 0", () => {
    expect(turnDirection(v(4, 0), v(3, 3))).toBe(1);
    expect(turnDirection(v(4, 0), v(-2, -4))).toBe(-1);
    expect(turnDirection(v(4, 0), v(-3, 0))).toBe(0);
    expect(turnDirection(v(4, 0), v(8, 0))).toBe(0);
  });
  it("gives the signed angle from a to b", () => {
    expect(signedAngle(v(4, 0), v(3, 3))).toBeCloseTo(45);
    expect(signedAngle(v(3, 3), v(4, 0))).toBeCloseTo(-45);
    expect(signedAngle(v(4, 0), v(-4, 0))).toBeCloseTo(180);
    expect(signedAngle(v(0, 0), v(4, 0))).toBeNull();
  });
  it("the inner product cannot tell left from right", () => {
    const a = v(4, 0);
    expect(inner(a, v(3, 3))).toBe(inner(a, v(3, -3)));
    expect(signedAngle(a, v(3, 3))).toBeCloseTo(-(signedAngle(a, v(3, -3)) as number));
  });
});

/** The formulas exactly as the original single-file page wrote them (reference/angle-explorer.original.html). */
function originalPairOf(p: { x: number; y: number }, q: { x: number; y: number }) {
  const dot = (a: typeof p, b: typeof p) => a.x * b.x + a.y * b.y;
  const len = (a: typeof p) => Math.hypot(a.x, a.y);
  const d = dot(p, q), lp = len(p), lq = len(q);
  const ok = lp > 1e-9 && lq > 1e-9;
  const n = ok ? Math.max(-1, Math.min(1, d / (lp * lq))) : 0;
  const sign = (ok ? Math.abs(n) < 0.004 : Math.abs(d) < 1e-9) ? 0 : d > 0 ? 1 : -1;
  const cross = p.x * q.y - p.y * q.x;
  const turn = !ok || Math.abs(cross) < 1e-6 * (1 + lp * lq) ? 0 : cross > 0 ? 1 : -1;
  const sdeg = ok ? (Math.atan2(cross, d) * 180) / Math.PI : null;
  return { d, lp, lq, ok, n, sign, cross, turn, sdeg };
}

describe("matches the original page", () => {
  const values = [-8, -5.5, -3, -1, -0.1, 0, 0.1, 1, 2.5, 4, 8];
  const extras = [v(1e-10, 0), v(0.003, 1), v(1, 0.0039), v(-8, 8), v(5, 5)];
  const vecs = [...values.flatMap((x) => values.map((y) => v(x, y))), ...extras];
  it(`agrees on all ${vecs.length ** 2} ordered pairs`, () => {
    for (const p of vecs) {
      for (const q of vecs) {
        const got = pairFacts(p, q);
        const want = originalPairOf(p, q);
        expect({ ...got, p: undefined, q: undefined }).toEqual({ ...want, p: undefined, q: undefined });
      }
    }
  });
});
