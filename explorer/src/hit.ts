// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/** Which vector is under the pointer. Pure, in paper coordinates. */
import type { ExplorerState } from "./state";

/** The tip within 0.85 steps of w (picked vectors win ties by 0.2), or −1. */
export function nearTip(st: ExplorerState, w: { x: number; y: number }): number {
  let best = -1;
  let bd = 1e9;
  st.vecs.forEach((v, i) => {
    const d = Math.hypot(v.x - w.x, v.y - w.y) - (st.sel.includes(i) ? 0.2 : 0);
    if (d < bd) {
      bd = d;
      best = i;
    }
  });
  return bd < 0.85 ? best : -1;
}

/** The arrow (shaft) within 0.45 steps of w, or −1. */
export function nearBody(st: ExplorerState, w: { x: number; y: number }): number {
  let best = -1;
  let bd = 1e9;
  st.vecs.forEach((v, i) => {
    const L2 = v.x * v.x + v.y * v.y;
    if (L2 < 1e-9) return;
    const t = Math.max(0, Math.min(1, (w.x * v.x + w.y * v.y) / L2));
    const d = Math.hypot(w.x - t * v.x, w.y - t * v.y);
    if (d < bd) {
      bd = d;
      best = i;
    }
  });
  return bd < 0.45 ? best : -1;
}
