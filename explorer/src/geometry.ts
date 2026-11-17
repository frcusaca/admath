// Copyright © 2026-present CAehi.us
/** Where things go on the plot's SVG canvas. Pure. */
import { SIZE } from "./state";

/** Width of the drawing area, in SVG units. */
export const W = 520;
/** One grid step, in SVG units. */
export const U = W / (2 * SIZE + 1);
/** The origin's SVG coordinate (both x and y). */
export const C = W / 2;
/** The plot's viewBox: a margin of 16 around the drawing area. */
export const VIEW_MIN = -16;
export const VIEW_SIZE = 552;

/** Paper x to SVG x. */
export const X = (x: number): number => C + x * U;
/** Paper y to SVG y (SVG y grows downward). */
export const Y = (y: number): number => C - y * U;

/** A pointer position (relative to the SVG's on-screen box) back to paper coordinates. */
export function toPaper(
  clientX: number,
  clientY: number,
  box: { left: number; top: number; width: number; height: number },
): { x: number; y: number } {
  const sx = ((clientX - box.left) / box.width) * VIEW_SIZE + VIEW_MIN;
  const sy = ((clientY - box.top) / box.height) * VIEW_SIZE + VIEW_MIN;
  return { x: (sx - C) / U, y: (C - sy) / U };
}
