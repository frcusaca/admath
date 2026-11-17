// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
import { describe, expect, it } from "vitest";
import { esc, fmt, fmtSignedDegrees, signClass } from "./format";

describe("fmt", () => {
  it("drops decimals on whole numbers and uses a real minus sign", () => {
    expect(fmt(4)).toBe("4");
    expect(fmt(4.00001)).toBe("4");
    expect(fmt(-3)).toBe("−3");
    expect(fmt(0.70710678)).toBe("0.71");
    expect(fmt(-0.5, 1)).toBe("−0.5");
    expect(fmt(-0.00001)).toBe("0");
  });
});

describe("fmtSignedDegrees", () => {
  it("shows + for counterclockwise, − for clockwise, nothing for no turn", () => {
    expect(fmtSignedDegrees(45, 1)).toBe("+45°");
    expect(fmtSignedDegrees(-45, -1)).toBe("−45°");
    expect(fmtSignedDegrees(180, 0)).toBe("180°");
    expect(fmtSignedDegrees(-0, 0)).toBe("0°");
    expect(fmtSignedDegrees(26.565, 1)).toBe("+26.6°");
  });
});

describe("signClass and esc", () => {
  it("maps signs to pos/neg/zero", () => {
    expect([signClass(2), signClass(0), signClass(-0.1)]).toEqual(["pos", "zero", "neg"]);
  });
  it("escapes HTML", () => {
    expect(esc(`<b a="1">'&'</b>`)).toBe("&lt;b a=&quot;1&quot;&gt;&#39;&amp;&#39;&lt;/b&gt;");
  });
});
