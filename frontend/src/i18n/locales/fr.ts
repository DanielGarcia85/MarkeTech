// frontend/src/i18n/locales/fr.ts
//
// French texts — translation of the interface
// ─────────────────────────────────────────────────────────────────────────────
// Must provide exactly the same keys as the English file: the type check
// fails if a key is missing or misspelled here.

import type en from "./en";

const fr: typeof en = {
  // Tagline and notice of the application
  app: {
    tagline:
      "Emplois et jobs d'étudiant en informatique, pour jeunes diplômés et étudiants.",
    notice: "Cette application est en cours de construction.",
  },

  // Header: session state
  header: {
    loggedInAs: "Connecté en tant que {email}",
    logout: "Se déconnecter",
  },

  // Language selector
  language: {
    label: "Langue",
  },

  // Status of the connection with the backend
  health: {
    label: "État de l'API :",
    checking: "Vérification…",
    online: "En ligne",
    offline: "Indisponible",
  },
};

export default fr;
