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

  // Development only: passes every request starting with /api or /_allauth
  // (authentication API) on to the Django backend, and the WebSocket /ws
  // (ws: true, which lets the switch of protocol through), so the browser
  // keeps talking to a single address. changeOrigin false keeps the Host
  // header of the browser (localhost:5173): Django checks it against the
  // Origin of every POST, and builds the links of its e-mails from it.
  server: {
    proxy: {
      "/api": { target: "http://localhost:8000", changeOrigin: false },
      "/_allauth": { target: "http://localhost:8000", changeOrigin: false },
      "/ws": { target: "ws://localhost:8000", ws: true, changeOrigin: false },
    },
  },
});
