// Copyright © 2026-present CAehi.us
/** The standalone page: one explorer that fills the page. */
import { COPYRIGHT } from "./copyright";
import { mountAngleExplorer } from "./mount";

mountAngleExplorer(document.body, { landmark: true, footer: COPYRIGHT });
