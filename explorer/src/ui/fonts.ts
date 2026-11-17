// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/**
 * The two typefaces (both SIL Open Font License, see THIRD_PARTY_NOTICES.md),
 * inlined as data URLs so the explorer works offline.
 *
 * Browsers ignore @font-face inside a shadow root, so these rules are added to the
 * document once, however many explorers the page holds.
 */
import atkinson400 from "@fontsource/atkinson-hyperlegible/files/atkinson-hyperlegible-latin-400-normal.woff2?inline";
import atkinson700 from "@fontsource/atkinson-hyperlegible/files/atkinson-hyperlegible-latin-700-normal.woff2?inline";
import mono400 from "@fontsource/jetbrains-mono/files/jetbrains-mono-latin-400-normal.woff2?inline";
import mono700 from "@fontsource/jetbrains-mono/files/jetbrains-mono-latin-700-normal.woff2?inline";

const FONT_STYLE_ID = "angle-explorer-fonts";

function face(family: string, weight: number, url: string): string {
  return `@font-face{font-family:"${family}";font-style:normal;font-weight:${weight};font-display:swap;src:url("${url}") format("woff2");}`;
}

export function installFonts(doc: Document): void {
  if (doc.getElementById(FONT_STYLE_ID)) return;
  const style = doc.createElement("style");
  style.id = FONT_STYLE_ID;
  style.textContent = [
    face("Atkinson Hyperlegible", 400, atkinson400),
    face("Atkinson Hyperlegible", 700, atkinson700),
    face("JetBrains Mono", 400, mono400),
    face("JetBrains Mono", 700, mono700),
  ].join("\n");
  doc.head.appendChild(style);
}
