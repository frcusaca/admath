// Copyright © 2026-present CAehi.us
import { describe, expect, it } from "vitest";
import { renderPlot } from "./render/plot";
import { renderReadout } from "./render/readout";
import { renderMatrix, renderVectorRows } from "./render/tables";
import { currentPair, createState } from "./state";

describe("names are escaped everywhere they are drawn", () => {
  const st = createState({ vectors: [[4, 0], [3, 3]], names: ["<img>", "b&"] });
  it.each([
    ["plot", renderPlot(st, false)],
    ["readout", renderReadout(currentPair(st), "<img>", "b&")],
    ["vector table", renderVectorRows(st, false)],
    ["pair table", renderMatrix(st)],
  ])("%s", (_, html) => {
    expect(html).not.toContain("<img>");
    expect(html).toContain("&lt;img&gt;");
  });
});

describe("blue and orange mean only the sign", () => {
  it("a right angle draws in ink with a square, not in blue or orange", () => {
    const st = createState({ vectors: [[4, 0], [0, 5]] });
    const svg = renderPlot(st, false);
    expect(svg).toContain('class="arc flat"');
    expect(svg).toContain('class="square"');
    expect(svg).not.toMatch(/class="(wedge|arc) (pos|neg)"/);
  });
  it("an acute and an obtuse angle use pos and neg", () => {
    expect(renderPlot(createState({ vectors: [[4, 0], [3, 3]] }), false)).toContain('class="arc pos"');
    expect(renderPlot(createState({ vectors: [[4, 0], [-4, 2]] }), false)).toContain('class="arc neg"');
  });
  it("the turn arrow is drawn in the sign colour, not a turn colour", () => {
    const left = renderPlot(createState({ vectors: [[4, 0], [3, 3]] }), false);
    const right = renderPlot(createState({ vectors: [[4, 0], [3, -3]] }), false);
    expect(left).toContain('<polygon class="pos"');
    expect(right).toContain('<polygon class="pos"');
  });
});
