/// <reference types="vitest/config" />
import { resolve } from "node:path";
import { defineConfig } from "vite";
import { viteSingleFile } from "vite-plugin-singlefile";

// Two builds from one source:
//   vite build --mode standalone   dist/standalone/angle-explorer.html (everything inlined)
//   vite build --mode lib          dist/lib/angle-explorer.js (ES module)
//                                  dist/lib/angle-explorer.iife.js (classic script; what Python embeds)
export default defineConfig(({ mode }) => {
  if (mode === "lib") {
    return {
      build: {
        outDir: "dist/lib",
        emptyOutDir: true,
        assetsInlineLimit: Number.MAX_SAFE_INTEGER,
        lib: {
          entry: resolve(import.meta.dirname, "src/index.ts"),
          name: "AngleExplorer",
          formats: ["es", "iife"],
          fileName: (format) => (format === "es" ? "angle-explorer.js" : "angle-explorer.iife.js"),
        },
      },
    };
  }
  return {
    plugins: mode === "standalone" ? [viteSingleFile()] : [],
    build: {
      outDir: "dist/standalone",
      emptyOutDir: true,
      assetsInlineLimit: Number.MAX_SAFE_INTEGER,
      rollupOptions: { input: resolve(import.meta.dirname, "index.html") },
    },
    test: {
      include: ["src/**/*.test.ts"],
    },
  };
});
