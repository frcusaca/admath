// Copyright © 2026-present CAehi.us
// SPDX-License-Identifier: LicenseRef-Prosperity-3.0.0
/** The standalone page: one explorer that fills the page. */
import { COPYRIGHT, LICENSE_NAME } from "./copyright";
import { mountAngleExplorer } from "./mount";

mountAngleExplorer(document.body, { landmark: true, footer: `${COPYRIGHT}. ${LICENSE_NAME}.` });
