// frontend/src/i18n/locales/en.ts
//
// English texts — reference language of the interface
// ─────────────────────────────────────────────────────────────────────────────
// Every text displayed by the application is declared here under a key.
// The other languages must provide exactly the same keys.

export default {
    // Tagline and notice of the application
  app: {
    tagline: "Tech jobs and student jobs for recent graduates and students.",
    notice: "This application is under construction.",
  },

  // Header: session state and links of the account
  header: {
    signup: "Sign up",
    loggedInAs: "Signed in as {email}",
    logout: "Log out",
  },

  // Sign-up page
  signup: {
    title: "Create your account",
    email: "E-mail address",
    password: "Password",
    role: "I am",
    candidate: "A candidate (student or recent graduate)",
    employer: "An employer",
    submit: "Create my account",
    sent: "We have sent an e-mail to {email}. Open it and follow its link to activate your account.",
  },

  // Messages shared by every form
  form: {
    failed: "Something went wrong. Please try again.",
    unreachable: "The server cannot be reached. Please try again later.",
  },

  // Language selector
  language: {
    label: "Language",
  },

  // Status of the connection with the backend
  health: {
    label: "API status:",
    checking: "Checking…",
    online: "Online",
    offline: "Unavailable",
  },
};
