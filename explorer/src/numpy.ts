/**
 * "Copy as NumPy": turn the explorer's vectors into Python a kid can paste
 * into a notebook cell. Pure, so it is unit-tested. Uses ASCII only: the
 * display minus sign (−) would be a syntax error in Python.
 */
import type { NamedVec } from "./state";

const PYTHON_KEYWORDS = new Set(
  (
    "False None True and as assert async await break class continue def del elif else except " +
    "finally for from global if import in is lambda nonlocal not or pass raise return try while with yield"
  ).split(" "),
);

/** Names that would also shadow the library the notebook just imported. */
const RESERVED = new Set(["np", "plt"]);

export function isPythonName(name: string): boolean {
  return /^[A-Za-z_][A-Za-z0-9_]*$/.test(name) && !PYTHON_KEYWORDS.has(name) && !RESERVED.has(name);
}

/** A number as Python source: at most 2 decimals, no trailing zeros, never "-0". */
export function pyNumber(v: number): string {
  let r = Math.round(v * 100) / 100;
  if (Object.is(r, -0)) r = 0;
  return String(r);
}

/**
 * One line per vector, `a = np.array([4, 0])`. If some name cannot be a Python
 * variable, everything goes into one matrix instead, one row per vector.
 */
export function toNumpy(vecs: readonly NamedVec[]): string {
  const row = (v: NamedVec) => `[${pyNumber(v.x)}, ${pyNumber(v.y)}]`;
  if (vecs.every((v) => isPythonName(v.n))) {
    return vecs.map((v) => `${v.n} = np.array(${row(v)})`).join("\n");
  }
  const names = vecs.map((v) => v.n.replace(/[\r\n]/g, " ")).join(", ");
  return `vectors = np.array([${vecs.map(row).join(", ")}])    # rows: ${names}`;
}
