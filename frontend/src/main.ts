// frontend/src/main.ts
//
// Application entry point — creates the Vue application and mounts it
// ─────────────────────────────────────────────────────────────────────────────
// Loaded by index.html. Everything the user sees is built from here.

import { createApp } from "vue";

import App from "./App.vue";

// Build the application from the root component and attach it to the
// element whose id is "app" in index.html
createApp(App).mount("#app");
