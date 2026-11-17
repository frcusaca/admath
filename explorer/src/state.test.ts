// Copyright © 2026-present CAehi.us
import { describe, expect, it } from "vitest";
import {
  addVector,
  chooseFirst,
  choosePair,
  chooseSecond,
  createState,
  dragTip,
  MAX_VECTORS,
  pick,
  removeVector,
  setCoordinate,
  swap,
} from "./state";

describe("createState", () => {
  it("starts with the original five vectors, a first and b second", () => {
    const st = createState();
    expect(st.vecs.map((v) => v.n).join("")).toBe("abcde");
    expect(st.vecs[1]).toEqual({ n: "b", x: 3, y: 3 });
    expect(st.sel).toEqual([0, 1]);
    expect(st.mode).toBe("norm");
    expect(st.snap).toBe(true);
  });
  it("takes vectors and names from options", () => {
    const st = createState({ vectors: [[1, 2], { x: -3, y: 0.5 }], names: ["u", "w"], second: 0, first: 1 });
    expect(st.vecs).toEqual([
      { n: "u", x: 1, y: 2 },
      { n: "w", x: -3, y: 0.5 },
    ]);
    expect(st.sel).toEqual([1, 0]);
  });
  it.each([
    [{ vectors: [[1, 2]] }, /2 to 8/],
    [{ vectors: [[1, 2], [1, 2, 3]] }, /2 numbers/],
    [{ vectors: [[1, 2], [9, 0]] }, /off the graph paper/],
    [{ vectors: [[1, 2], [Number.NaN, 0]] }, /finite/],
    [{ vectors: [[1, 2], [3, 4]], names: ["a"] }, /need 2 names/],
    [{ vectors: [[1, 2], [3, 4]], names: ["a", "a"] }, /own name/],
    [{ vectors: [[1, 2], [3, 4]], first: 1, second: 1 }, /different/],
  ])("rejects bad options %#", (opts, message) => {
    expect(() => createState(opts as never)).toThrow(message);
  });
});

describe("picking", () => {
  it("tapping makes a vector the second, and the old second becomes first", () => {
    const st = createState();
    expect(pick(st, 3)).toBe(true);
    expect(st.sel).toEqual([1, 3]);
    expect(pick(st, 3)).toBe(false);
  });
  it("radio buttons swap when you pick the other slot's vector", () => {
    const st = createState();
    chooseFirst(st, 1);
    expect(st.sel).toEqual([1, 0]);
    chooseSecond(st, 1);
    expect(st.sel).toEqual([0, 1]);
    chooseSecond(st, 4);
    expect(st.sel).toEqual([0, 4]);
  });
  it("the diagonal of the pair table does nothing", () => {
    const st = createState();
    expect(choosePair(st, 2, 2)).toBe(false);
    expect(choosePair(st, 2, 4)).toBe(true);
    expect(st.sel).toEqual([2, 4]);
    swap(st);
    expect(st.sel).toEqual([4, 2]);
  });
});

describe("editing", () => {
  it("typing clamps to the paper and treats junk as 0", () => {
    const st = createState();
    setCoordinate(st, 0, "x", "12");
    setCoordinate(st, 0, "y", "");
    expect(st.vecs[0]).toMatchObject({ x: 8, y: 0 });
  });
  it("dragging snaps to whole numbers, or tenths with snap off", () => {
    const st = createState();
    expect(dragTip(st, 0, 2.4, 1.6)).toBe(true);
    expect(st.vecs[0]).toMatchObject({ x: 2, y: 2 });
    expect(dragTip(st, 0, 2.2, 1.9)).toBe(false);
    st.snap = false;
    dragTip(st, 0, 2.44, -9.7);
    expect(st.vecs[0]).toMatchObject({ x: 2.4, y: -8 });
  });
  it("dragging an unpicked vector picks it", () => {
    const st = createState();
    dragTip(st, 3, -3, 3);
    expect(st.sel).toEqual([1, 3]);
  });
});

describe("adding and removing", () => {
  it("adds the next free letter at the first free spot, as the second vector", () => {
    const st = createState();
    expect(addVector(st)).toBe(true);
    expect(st.vecs[5]).toEqual({ n: "f", x: 2, y: -3 });
    expect(st.sel).toEqual([1, 5]);
  });
  it("stops at 8 vectors", () => {
    const st = createState();
    while (addVector(st)) {
      /* fill up */
    }
    expect(st.vecs.length).toBe(MAX_VECTORS);
  });
  it("never removes below 2, and keeps two different picks", () => {
    const st = createState({ vectors: [[1, 0], [0, 1], [1, 1]] });
    st.sel = [1, 2];
    removeVector(st, 1);
    expect(st.vecs.map((v) => v.n)).toEqual(["a", "c"]);
    expect(st.sel[0]).not.toBe(st.sel[1]);
    expect(removeVector(st, 0)).toBe(false);
  });
  it("matches the original rule when the last vector goes", () => {
    const st = createState();
    st.sel = [3, 4];
    removeVector(st, 4);
    expect(st.sel).toEqual([0, 3]);
  });
});
