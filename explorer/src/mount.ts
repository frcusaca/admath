// Copyright © 2026-present CAehi.us
/**
 * mountAngleExplorer(element, options): put an Angle Explorer inside `element`.
 *
 * The explorer lives in a shadow root on `element`, so several can share a page
 * and none of them is affected by the page's CSS.
 */
import { toPaper } from "./geometry";
import { nearBody, nearTip } from "./hit";
import { length } from "./math";
import { toNumpy } from "./numpy";
import { renderPlot } from "./render/plot";
import { renderMeter, renderReadout } from "./render/readout";
import { matrixHint, renderMatrix, renderVectorRows } from "./render/tables";
import { nearestTracePoint, renderTrace, traceTip, type TracePoint } from "./render/trace";
import { fmt } from "./format";
import {
  addVector,
  canAdd,
  chooseFirst,
  choosePair,
  chooseSecond,
  createState,
  currentPair,
  dragTip,
  pick,
  removeVector,
  setCoordinate,
  swap,
  type ExplorerState,
  type NamedVec,
  type StateOptions,
} from "./state";
import { installFonts } from "./ui/fonts";
import css from "./ui/styles.css?inline";
import { template } from "./ui/template";

export type Theme = "auto" | "light" | "dark";

export interface MountOptions extends StateOptions {
  /** "auto" (default) follows the reader's system setting. */
  theme?: Theme;
  /** Show the title and the one-line introduction (default true). */
  header?: boolean;
  /** Use a <main> landmark. Only for a page that holds nothing else (default false). */
  landmark?: boolean;
  /** A line of small print at the bottom, e.g. the copyright notice (default none). */
  footer?: string;
}

export interface AngleExplorerHandle {
  /** The vectors as they are now: names and coordinates. */
  getVectors(): { name: string; x: number; y: number }[];
  /** The same Python code that "Copy as NumPy" gives. */
  toNumpy(): string;
  /** Stop any animation and remove the explorer from the element. */
  destroy(): void;
}

/** One spin of the second vector: which vector, where it started, and the animation frame. */
interface Spin {
  j: number;
  o: NamedVec;
  raf: number;
}

interface Drag {
  i: number;
  moved: boolean;
  body: number;
}

export function mountAngleExplorer(element: HTMLElement, options: MountOptions = {}): AngleExplorerHandle {
  const st: ExplorerState = createState(options);
  const doc = element.ownerDocument;
  const win = doc.defaultView ?? window;
  installFonts(doc);

  const theme = options.theme ?? "auto";
  if (theme === "auto") element.removeAttribute("data-theme");
  else element.setAttribute("data-theme", theme);

  const root = element.shadowRoot ?? element.attachShadow({ mode: "open" });
  const sheet = doc.createElement("style");
  sheet.textContent = css;
  root.replaceChildren(sheet);
  const holder = doc.createElement("div");
  holder.innerHTML = template({
    landmark: options.landmark ?? false,
    header: options.header ?? true,
    footer: options.footer ?? null,
  });
  root.append(...holder.childNodes);

  const $ = <T extends Element = HTMLElement>(id: string): T => {
    const el = root.getElementById(id);
    if (!el) throw new Error(`Angle Explorer: missing #${id}`);
    return el as unknown as T;
  };
  const svg = $<SVGSVGElement>("plot");
  const traceSvg = $<SVGSVGElement>("trace");
  const vt = $<HTMLTableElement>("vt");
  const spinBtn = $<HTMLButtonElement>("spin");
  const swapBtn = $<HTMLButtonElement>("swap");
  const addBtn = $<HTMLButtonElement>("add");
  const copyBtn = $<HTMLButtonElement>("copy");
  const copyBox = $("copybox");
  const copyMsg = $("copymsg");
  const code = $<HTMLTextAreaElement>("code");
  const snapBox = $<HTMLInputElement>("snap");

  let trace: TracePoint[] = [];
  let hover: TracePoint | null = null;
  let spin: Spin | null = null;
  let drag: Drag | null = null;
  let copied: string | null = null;
  let destroyed = false;

  const names = () => {
    const pr = currentPair(st);
    return [(pr.p as NamedVec).n, (pr.q as NamedVec).n] as const;
  };
  const resetTrace = () => {
    trace = [];
    hover = null;
  };

  // ---- rendering ---------------------------------------------------------

  function drawPlot() {
    svg.innerHTML = renderPlot(st, spin !== null);
  }

  function drawTrace() {
    const [a, b] = names();
    traceSvg.innerHTML = renderTrace(currentPair(st), a, b, trace, hover);
    $("tip").textContent = traceTip(a, b, trace, hover);
  }

  function drawRead() {
    const pr = currentPair(st);
    const [a, b] = names();
    $("read").innerHTML = renderReadout(pr, a, b);
    $("meter").innerHTML = renderMeter(pr);
    spinBtn.textContent = spin ? "Stop" : `Spin ${b} once around`;
    spinBtn.disabled = !pr.ok && !spin;
    swapBtn.disabled = spin !== null;
    drawTrace();
  }

  function drawTable() {
    (vt.tBodies[0] as HTMLTableSectionElement).innerHTML = renderVectorRows(st, spin !== null);
    addBtn.disabled = !canAdd(st) || spin !== null;
    copyBtn.disabled = spin !== null;
  }

  function drawMatrix() {
    const raw = st.mode === "raw";
    $("gm").innerHTML = renderMatrix(st);
    $("mraw").setAttribute("aria-pressed", String(raw));
    $("mnorm").setAttribute("aria-pressed", String(!raw));
    $("gmhint").textContent = matrixHint(st);
  }

  function drawCopy() {
    if (copied === null) return;
    if (toNumpy(st.vecs) !== copied) {
      copyMsg.textContent = "The vectors changed since you copied. Press Copy as NumPy again.";
    }
  }

  /**
   * Redraw everything. Rebuilding a table replaces its buttons and inputs; if one
   * of them had keyboard focus, give focus to its replacement (same id).
   */
  function drawAll() {
    const focusedId = root.activeElement?.id ?? "";
    drawPlot();
    drawRead();
    drawTable();
    drawMatrix();
    drawCopy();
    if (focusedId && !root.activeElement) {
      const again = root.getElementById(focusedId) as HTMLElement | null;
      if (again && !(again as HTMLButtonElement).disabled) again.focus({ preventScroll: true });
    }
  }

  // ---- the plot: drag a tip, tap an arrow ---------------------------------

  const paperPoint = (e: PointerEvent) => toPaper(e.clientX, e.clientY, svg.getBoundingClientRect());

  svg.addEventListener("pointerdown", (e) => {
    if (spin) return;
    const w = paperPoint(e);
    const i = nearTip(st, w);
    drag = { i, moved: false, body: i < 0 ? nearBody(st, w) : -1 };
    if (i >= 0) {
      svg.setPointerCapture(e.pointerId);
      e.preventDefault();
    }
  });
  svg.addEventListener("pointermove", (e) => {
    if (!drag || drag.i < 0) return;
    const w = paperPoint(e);
    if (!dragTip(st, drag.i, w.x, w.y)) return;
    drag.moved = true;
    resetTrace();
    drawAll();
  });
  svg.addEventListener("pointerup", () => {
    if (!drag) return;
    if (drag.i >= 0 && !drag.moved) {
      if (pick(st, drag.i)) resetTrace();
    } else if (drag.i < 0 && drag.body >= 0) {
      if (pick(st, drag.body)) resetTrace();
    }
    drag = null;
    drawAll();
  });
  svg.addEventListener("pointercancel", () => {
    drag = null;
  });

  // ---- the curve: hover or tap to read a point -----------------------------

  const traceHover = (e: PointerEvent) => {
    hover = nearestTracePoint(trace, e.clientX, traceSvg.getBoundingClientRect());
    drawTrace();
  };
  traceSvg.addEventListener("pointermove", traceHover);
  traceSvg.addEventListener("pointerdown", traceHover);
  traceSvg.addEventListener("pointerleave", () => {
    hover = null;
    drawTrace();
  });

  // ---- the vector table ---------------------------------------------------

  vt.addEventListener("input", (e) => {
    const el = e.target as HTMLInputElement;
    const k = el.dataset?.k;
    if (k !== "x" && k !== "y") return;
    const i = Number(el.dataset.i);
    setCoordinate(st, i, k, el.value);
    resetTrace();
    drawPlot();
    drawRead();
    drawMatrix();
    drawCopy();
    const v = st.vecs[i];
    if (v) $("vl" + i).textContent = fmt(length(v));
  });
  vt.addEventListener("change", (e) => {
    const d = (e.target as HTMLElement).dataset;
    if (!d || spin) return;
    if (d.first !== undefined) chooseFirst(st, Number(d.first));
    else if (d.second !== undefined) chooseSecond(st, Number(d.second));
    else return;
    resetTrace();
    drawAll();
  });
  vt.addEventListener("click", (e) => {
    const b = (e.target as Element).closest("button");
    if (!b || spin || b.dataset.del === undefined) return;
    const i = Number(b.dataset.del);
    // the removed row's button is gone; keep keyboard users in the table
    const next = Math.min(i, st.vecs.length - 2);
    if (!removeVector(st, i)) return;
    resetTrace();
    drawAll();
    const target = (root.getElementById(`del${next}`) ?? root.getElementById(`f${next}`)) as HTMLElement | null;
    if (root.activeElement === null && target) target.focus({ preventScroll: true });
  });
  addBtn.addEventListener("click", () => {
    if (spin || !addVector(st)) return;
    resetTrace();
    drawAll();
  });

  // ---- Copy as NumPy --------------------------------------------------------

  copyBtn.addEventListener("click", () => {
    if (spin) return;
    const text = toNumpy(st.vecs);
    copied = text;
    code.value = text;
    code.rows = Math.max(2, text.split("\n").length);
    copyBox.hidden = false;
    const done = (ok: boolean) => {
      if (copied !== text) return;
      copyMsg.textContent = ok
        ? "Copied. Paste it into a code cell."
        : "Select the code below and copy it (Ctrl+C, or ⌘C on a Mac). Then paste it into a code cell.";
      if (!ok) {
        code.focus();
        code.select();
      }
    };
    const fallback = () => {
      // Older browsers, and some notebook output frames, block the clipboard API.
      code.focus();
      code.select();
      let ok = false;
      try {
        ok = doc.execCommand("copy");
      } catch {
        ok = false;
      }
      copyBtn.focus({ preventScroll: true });
      done(ok);
    };
    const clip = win.navigator.clipboard;
    if (clip && typeof clip.writeText === "function") {
      clip.writeText(text).then(() => done(true), fallback);
    } else {
      fallback();
    }
  });
  code.addEventListener("focus", () => code.select());

  // ---- the pair table, swap, raw/normalized, snap ---------------------------

  $("gm").addEventListener("click", (e) => {
    const b = (e.target as Element).closest("button");
    if (!b || spin) return;
    if (!choosePair(st, Number(b.dataset.i), Number(b.dataset.j))) return;
    resetTrace();
    drawAll();
  });
  swapBtn.addEventListener("click", () => {
    if (spin) return;
    swap(st);
    resetTrace();
    drawAll();
  });
  $("mraw").addEventListener("click", () => {
    st.mode = "raw";
    drawMatrix();
  });
  $("mnorm").addEventListener("click", () => {
    st.mode = "norm";
    drawMatrix();
  });
  snapBox.addEventListener("change", () => {
    st.snap = snapBox.checked;
  });

  // ---- Spin: turn the second vector once around, tracing the curve --------

  function stopSpin() {
    if (!spin) return;
    win.cancelAnimationFrame(spin.raf);
    Object.assign(st.vecs[spin.j] as NamedVec, spin.o);
    spin = null;
    if (!destroyed) drawAll();
  }

  spinBtn.addEventListener("click", () => {
    if (spin) {
      stopSpin();
      return;
    }
    const pr = currentPair(st);
    if (!pr.ok) return;
    const j = st.sel[1];
    const target = st.vecs[j] as NamedVec;
    const o = { ...target };
    const L = length(o);
    const t0 = Math.atan2(o.y, o.x);
    resetTrace();
    const step = (deg: number) => {
      const t = t0 + (deg * Math.PI) / 180;
      target.x = L * Math.cos(t);
      target.y = L * Math.sin(t);
      const now = currentPair(st);
      trace.push({ s: now.sdeg ?? 0, n: now.n });
    };
    if (win.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      // No animation: draw the whole curve at once.
      for (let d = 0; d <= 360; d += 2) step(d);
      Object.assign(target, o);
      drawAll();
      return;
    }
    let t1: number | null = null;
    const current: Spin = { j, o, raf: 0 };
    spin = current;
    const tick = (ts: number) => {
      if (spin !== current) return;
      if (t1 === null) t1 = ts;
      const deg = Math.min(360, ((ts - t1) / 7000) * 360);
      step(deg);
      drawPlot();
      drawRead();
      drawMatrix();
      if (deg < 360) current.raf = win.requestAnimationFrame(tick);
      else stopSpin();
    };
    drawTable();
    current.raf = win.requestAnimationFrame(tick);
  });

  // ---- start ---------------------------------------------------------------

  snapBox.checked = st.snap;
  drawAll();

  return {
    getVectors: () => st.vecs.map((v) => ({ name: v.n, x: v.x, y: v.y })),
    toNumpy: () => toNumpy(st.vecs),
    destroy: () => {
      destroyed = true;
      stopSpin();
      root.replaceChildren();
    },
  };
}
