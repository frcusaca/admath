// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/** Number and text formatting shared by every view. Pure functions. */
import type { Sign } from "./math";

const MINUS = "−";

/**
 * A number for display: whole numbers without decimals, others with `places`,
 * and a real minus sign (−) instead of a hyphen.
 */
export function fmt(value: number, places = 2): string {
  let v = value;
  if (Math.abs(v - Math.round(v)) < 1e-4) v = Math.round(v);
  if (Object.is(v, -0)) v = 0;
  const s = Number.isInteger(v) ? String(v) : v.toFixed(places);
  return s.replace("-", MINUS);
}

/** An angle with a + for counterclockwise; no sign when there is no turn. */
export function fmtSignedDegrees(deg: number, turn: Sign): string {
  if (turn === 0) return fmt(Math.abs(deg), 1) + "°";
  return (deg > 0 ? "+" : "") + fmt(deg, 1) + "°";
}

/** The CSS class for a sign: blue, orange, or neither. */
export function signClass(s: number): "pos" | "neg" | "zero" {
  return s > 0 ? "pos" : s < 0 ? "neg" : "zero";
}

/** Escape text for HTML element content and attribute values. */
export function esc(text: string): string {
  return text
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}
