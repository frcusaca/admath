// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
import { describe, expect, it } from "vitest";
import { isPythonName, pyNumber, toNumpy } from "./numpy";

describe("Copy as NumPy", () => {
  it("writes one line per vector", () => {
    expect(
      toNumpy([
        { n: "a", x: 4, y: 0 },
        { n: "b", x: -3, y: 2.5 },
      ]),
    ).toBe("a = np.array([4, 0])\nb = np.array([-3, 2.5])");
  });
  it("uses ASCII minus and at most 2 decimals, never -0", () => {
    expect(pyNumber(-1.23456)).toBe("-1.23");
    expect(pyNumber(-0.001)).toBe("0");
    expect(pyNumber(2.999)).toBe("3");
    const code = toNumpy([{ n: "a", x: -Math.SQRT2, y: 0 }]);
    expect(code).not.toMatch(/−/);
  });
  it("a name cannot smuggle code into the pasted line (SECURITY.md SEC-011)", () => {
    const code = toNumpy([
      { n: "a\nimport os; os.system('x')", x: 1, y: 2 },
      { n: "b\r\nprint(1)", x: 3, y: 4 },
    ]);
    expect(code.split("\n")).toHaveLength(1);            // one line: nothing runs after the comment
    expect(code.startsWith("vectors = np.array([[1, 2], [3, 4]])    # rows:")).toBe(true);
  });
  it("falls back to one matrix when a name is not a Python variable", () => {
    expect(isPythonName("knight")).toBe(true);
    expect(isPythonName("my vec")).toBe(false);
    expect(isPythonName("if")).toBe(false);
    expect(isPythonName("np")).toBe(false);
    expect(isPythonName("2a")).toBe(false);
    expect(
      toNumpy([
        { n: "a", x: 1, y: 2 },
        { n: "my vec", x: 3, y: 4 },
      ]),
    ).toBe("vectors = np.array([[1, 2], [3, 4]])    # rows: a, my vec");
  });
});
