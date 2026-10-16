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
    login: "Log in",
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
    haveAccount: "Already have an account?",
    loginLink: "Log in",
  },

  // Login page
  login: {
    title: "Log in",
    email: "E-mail address",
    password: "Password",
    submit: "Log in",
    unverified: "Your e-mail address is not verified yet. Open the e-mail we sent you and follow its link, then log in again.",
    noAccount: "No account yet?",
    signupLink: "Sign up",
  },

  // Address verification page, reached from the link in the e-mail
  verify: {
    title: "E-mail address verification",
    pending: "Checking your link…",
    confirmed: "Your e-mail address is confirmed. You can now log in.",
    invalid: "This link is invalid or has expired. Log in: if your address is still unconfirmed, you will receive a new link.",
    loginLink: "Log in",
  },

  // Messages shared by every form
  form: {
    failed: "Something went wrong. Please try again.",
    unreachable: "The server cannot be reached. Please try again later.",
    tooMany: "Too many attempts. Please wait a moment and try again.",
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
