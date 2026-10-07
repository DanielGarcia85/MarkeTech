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
});
