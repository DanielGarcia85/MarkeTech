// frontend/vite.config.ts
//
// Vite configuration — development server and production build
// ─────────────────────────────────────────────────────────────────────────────
// Vite serves the application with hot reload during development and bundles
// it into static files for production.

import vue from "@vitejs/plugin-vue";
import { defineConfig } from "vite";

export default defineConfig({
  // Lets Vite understand single-file components (.vue)
  plugins: [vue()],

  // Keeps the path used to open the project instead of replacing symbolic
  // links with their real location. Required to run the dev server through
  // a link, because Vite cannot serve files from a path that contains "#",
  // which is the case of the OneDrive folder where this project is stored.
  resolve: { preserveSymlinks: true },
});
