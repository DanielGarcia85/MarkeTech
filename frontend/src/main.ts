// frontend/src/main.ts
//
// Application entry point — creates the Vue application and mounts it
// ─────────────────────────────────────────────────────────────────────────────
// Loaded by index.html. Everything the user sees is built from here.

import { createApp } from "vue";

// Poppins, the font of the interface, served from our own files: the Latin
// characters (enough for English and French) in two weights, regular for
// the text and semi-bold for titles and buttons
import "@fontsource/poppins/latin-400.css";
import "@fontsource/poppins/latin-600.css";

import App from "./App.vue";
import { i18n } from "./i18n";
import { router } from "./router";
import "./style.css";

// Build the application from the root component, plug in the translation
// engine and the router, then attach it to the element whose id is "app"
// in index.html
createApp(App).use(i18n).use(router).mount("#app");
