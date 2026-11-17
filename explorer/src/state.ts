// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/**
 * The explorer's state and every change a person can make to it.
 * The functions mutate the state they are given (the views re-render from it)
 * and return whether anything changed. They touch no DOM, so they are unit-tested.
 */
import { pairFacts, type PairFacts } from "./math";

/** The graph paper runs from −SIZE to SIZE. */
export const SIZE = 8;
/** Default names, and the most vectors there can be. */
export const NAMES = "abcdefgh";
export const MAX_VECTORS = NAMES.length;
export const MAX_NAME_LENGTH = 8;

export interface NamedVec {
  n: string;
  x: number;
  y: number;
}

export type MatrixMode = "raw" | "norm";

export interface ExplorerState {
  vecs: NamedVec[];
  /** [first, second]: indexes into vecs, always different */
  sel: [number, number];
  mode: MatrixMode;
  snap: boolean;
}

export type VectorInput = readonly [number, number] | readonly number[] | { readonly x: number; readonly y: number };

export interface StateOptions {
  /** Starting vectors, 2 to 8 of them, each [x, y] with −8 ≤ x, y ≤ 8. */
  vectors?: readonly VectorInput[];
  /** One name per vector. Defaults to a, b, c, … */
  names?: readonly string[];
  /** Index of the first vector (default 0). */
  first?: number;
  /** Index of the second vector (default 1). */
  second?: number;
  /** "norm" (default) or "raw" for the table of pairs. */
  mode?: MatrixMode;
  /** Snap dragged tips to whole numbers (default true). */
  snap?: boolean;
}

export const DEFAULT_VECTORS: readonly (readonly [number, number])[] = [
  [4, 0],
  [3, 3],
  [0, 5],
  [-4, 2],
  [-2, -4],
];

function toXY(v: VectorInput, index: number): { x: number; y: number } {
  let x: unknown;
  let y: unknown;
  if (Array.isArray(v)) {
    if (v.length !== 2) throw new Error(`Angle Explorer: vector ${index + 1} must have 2 numbers, not ${v.length}.`);
    [x, y] = v;
  } else {
    ({ x, y } = v as { x: unknown; y: unknown });
  }
  if (typeof x !== "number" || typeof y !== "number" || !Number.isFinite(x) || !Number.isFinite(y)) {
    throw new Error(`Angle Explorer: vector ${index + 1} must hold two finite numbers.`);
  }
  if (Math.abs(x) > SIZE || Math.abs(y) > SIZE) {
    throw new Error(`Angle Explorer: vector ${index + 1} is off the graph paper (−${SIZE} to ${SIZE}).`);
  }
  return { x, y };
}

/** Build a valid starting state, or throw an Error that says what is wrong. */
export function createState(options: StateOptions = {}): ExplorerState {
  const inputs = options.vectors ?? DEFAULT_VECTORS;
  if (inputs.length < 2 || inputs.length > MAX_VECTORS) {
    throw new Error(`Angle Explorer: give 2 to ${MAX_VECTORS} vectors, not ${inputs.length}.`);
  }
  const names = options.names ?? [...NAMES.slice(0, inputs.length)];
  if (names.length !== inputs.length) {
    throw new Error(`Angle Explorer: ${inputs.length} vectors need ${inputs.length} names, not ${names.length}.`);
  }
  if (new Set(names).size !== names.length) throw new Error("Angle Explorer: every vector needs its own name.");
  for (const n of names) {
    if (typeof n !== "string" || n.trim() === "" || n.length > MAX_NAME_LENGTH) {
      throw new Error(`Angle Explorer: names must be 1 to ${MAX_NAME_LENGTH} characters.`);
    }
  }
  const vecs = inputs.map((v, i) => ({ n: names[i] as string, ...toXY(v, i) }));
  const first = options.first ?? 0;
  const second = options.second ?? (first === 1 ? 0 : 1);
  const okIndex = (i: number) => Number.isInteger(i) && i >= 0 && i < vecs.length;
  if (!okIndex(first) || !okIndex(second) || first === second) {
    throw new Error("Angle Explorer: first and second must be two different vector indexes.");
  }
  return { vecs, sel: [first, second], mode: options.mode ?? "norm", snap: options.snap ?? true };
}

export function currentPair(st: ExplorerState): PairFacts {
  return pairAt(st, st.sel[0], st.sel[1]);
}

export function pairAt(st: ExplorerState, i: number, j: number): PairFacts {
  return pairFacts(st.vecs[i] as NamedVec, st.vecs[j] as NamedVec);
}

const clamp = (v: number) => Math.max(-SIZE, Math.min(SIZE, v));

/** Tapping a vector makes it the second one. The old second becomes the first. */
export function pick(st: ExplorerState, i: number): boolean {
  if (i === st.sel[1]) return false;
  st.sel = [st.sel[1], i];
  return true;
}

/** The "1st" radio button. Picking the current second swaps the two. */
export function chooseFirst(st: ExplorerState, i: number): boolean {
  const before = st.sel;
  st.sel = i === st.sel[1] ? [i, st.sel[0]] : [i, st.sel[1]];
  return st.sel[0] !== before[0] || st.sel[1] !== before[1];
}

/** The "2nd" radio button. Picking the current first swaps the two. */
export function chooseSecond(st: ExplorerState, i: number): boolean {
  const before = st.sel;
  st.sel = i === st.sel[0] ? [st.sel[1], i] : [st.sel[0], i];
  return st.sel[0] !== before[0] || st.sel[1] !== before[1];
}

/** A square in the table of pairs: row is first, column is second. The diagonal does nothing. */
export function choosePair(st: ExplorerState, i: number, j: number): boolean {
  if (i === j) return false;
  st.sel = [i, j];
  return true;
}

export function swap(st: ExplorerState): void {
  st.sel = [st.sel[1], st.sel[0]];
}

/** Typing into the x or y box. Empty or bad input counts as 0; values are kept on the paper. */
export function setCoordinate(st: ExplorerState, i: number, key: "x" | "y", raw: string): void {
  const v = st.vecs[i];
  if (!v) return;
  const val = parseFloat(raw);
  v[key] = Number.isFinite(val) ? clamp(val) : 0;
}

/** Dragging a tip to a point on the paper. Returns false if the tip did not move. */
export function dragTip(st: ExplorerState, i: number, wx: number, wy: number): boolean {
  const v = st.vecs[i];
  if (!v) return false;
  const q = st.snap ? 1 : 10;
  const x = clamp(Math.round(wx * q) / q);
  const y = clamp(Math.round(wy * q) / q);
  if (x === v.x && y === v.y) return false;
  v.x = x;
  v.y = y;
  if (!st.sel.includes(i)) pick(st, i);
  return true;
}

/** The spots tried, in order, for a new vector. */
const NEW_SPOTS: readonly (readonly [number, number])[] = [
  [2, -3],
  [-5, -1],
  [6, 2],
  [-1, 6],
  [5, -5],
  [-6, 5],
];

export function canAdd(st: ExplorerState): boolean {
  return st.vecs.length < MAX_VECTORS && nextName(st) !== undefined;
}

function nextName(st: ExplorerState): string | undefined {
  const used = st.vecs.map((v) => v.n);
  return [...NAMES].find((c) => !used.includes(c));
}

/** Add a vector with the next free letter, at the first free spot, and make it the second. */
export function addVector(st: ExplorerState): boolean {
  if (st.vecs.length >= MAX_VECTORS) return false;
  const n = nextName(st);
  if (n === undefined) return false;
  const s = NEW_SPOTS.find(([x, y]) => !st.vecs.some((v) => v.x === x && v.y === y)) ?? [1, 1];
  st.vecs.push({ n, x: s[0], y: s[1] });
  pick(st, st.vecs.length - 1);
  return true;
}

export function canRemove(st: ExplorerState): boolean {
  return st.vecs.length > 2;
}

/** Remove a vector, keeping two different vectors picked. */
export function removeVector(st: ExplorerState, i: number): boolean {
  if (!canRemove(st) || i < 0 || i >= st.vecs.length) return false;
  st.vecs.splice(i, 1);
  const last = st.vecs.length - 1;
  const moved = st.sel.map((s) => Math.min(s > i ? s - 1 : s, last)) as [number, number];
  st.sel = moved[0] === moved[1] ? (moved[1] === 0 ? [1, 0] : [0, moved[1]]) : moved;
  return true;
}
