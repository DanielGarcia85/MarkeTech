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
    tagline: "Emplois et jobs d'étudiant en informatique, pour jeunes diplômés et étudiants.",
    notice: "Cette application est en cours de construction.",
  },

  // Header: session state and links of the account
  header: {
    signup: "S'inscrire",
    login: "Se connecter",
    loggedInAs: "Connecté en tant que {email}",
    logout: "Se déconnecter",
  },

  // Sign-up page
  signup: {
    title: "Créer votre compte",
    email: "Adresse e-mail",
    password: "Mot de passe",
    role: "Je suis",
    candidate: "Candidat (étudiant ou jeune diplômé)",
    employer: "Employeur",
    submit: "Créer mon compte",
    sent: "Nous avons envoyé un e-mail à {email}. Ouvrez-le et suivez son lien pour activer votre compte.",
    haveAccount: "Déjà un compte ?",
    loginLink: "Se connecter",
  },

  // Login page
  login: {
    title: "Se connecter",
    email: "Adresse e-mail",
    password: "Mot de passe",
    submit: "Se connecter",
    unverified: "Votre adresse e-mail n'est pas encore vérifiée. Ouvrez l'e-mail que nous vous avons envoyé et suivez son lien, puis reconnectez-vous.",
    noAccount: "Pas encore de compte ?",
    signupLink: "S'inscrire",
    forgotLink: "Mot de passe oublié ?",
  },

  // Address verification page, reached from the link in the e-mail
  verify: {
    title: "Vérification de l'adresse e-mail",
    pending: "Vérification de votre lien…",
    confirmed: "Votre adresse e-mail est confirmée. Vous pouvez maintenant vous connecter.",
    invalid: "Ce lien n'est pas valable ou a expiré. Connectez-vous : si votre adresse n'est pas encore confirmée, vous recevrez un nouveau lien.",
    loginLink: "Se connecter",
  },

  // Password reset: the page that asks for the link
  passwordReset: {
    title: "Réinitialiser votre mot de passe",
    intro: "Indiquez votre adresse e-mail : nous vous enverrons un lien pour choisir un nouveau mot de passe.",
    email: "Adresse e-mail",
    submit: "Envoyer le lien",
    sent: "Nous avons envoyé un e-mail à {email}. Ouvrez-le et suivez son lien pour choisir un nouveau mot de passe.",
  },

  // Password reset: the page reached from the link in the e-mail
  newPassword: {
    title: "Choisir un nouveau mot de passe",
    password: "Nouveau mot de passe",
    submit: "Enregistrer le nouveau mot de passe",
    done: "Votre mot de passe est changé. Vous pouvez maintenant vous connecter.",
    invalid: "Ce lien n'est pas valable ou a expiré.",
    requestLink: "Demander un nouveau lien",
    loginLink: "Se connecter",
  },

  // Messages shared by every form
  form: {
    failed: "Une erreur est survenue. Veuillez réessayer.",
    unreachable: "Le serveur est injoignable. Veuillez réessayer plus tard.",
    tooMany: "Trop de tentatives. Patientez un instant avant de réessayer.",
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
