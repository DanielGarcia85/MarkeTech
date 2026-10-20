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

  // The two roles, as shown to the logged-in user (header menu, profile)
  roles: {
    candidate: "Candidat",
    employer: "Employeur",
  },

  // Header: session state and links of the account
  header: {
    signup: "S'inscrire",
    login: "Se connecter",
    profile: "Mon profil",
    account: "Menu du compte",
    logout: "Se déconnecter",
  },

  // Side bar: the navigation of a logged-in user, one group per area
  nav: {
    label: "Navigation principale",
    offers: "Offres",
    allOffers: "Toutes les offres",
    myOffers: "Mes offres",
    myApplications: "Mes candidatures",
    account: "Mon compte",
    profile: "Profil",
  },

  // Footer: who is behind the site, where to find more, how to get in touch
  footer: {
    about: "MarkeTech est un projet de démonstration, sans activité commerciale,\nréécrit par Daniel Garcia à partir d'un projet d'équipe de la HEG Genève.",
    github: "GitHub",
    linkedin: "LinkedIn",
    portfolio: "Portfolio",
    contact: "Contact",
    terms: "Conditions d'utilisation",
    privacy: "Confidentialité",
    copyright: "© {year} Daniel Garcia",
  },

  // Sign-up page
  signup: {
    title: "Créer votre compte",
    firstName: "Prénom",
    lastName: "Nom",
    email: "Adresse e-mail",
    password: "Mot de passe",
    passwordConfirm: "Confirmez le mot de passe",
    role: "Je suis",
    candidate: "Candidat",
    employer: "Employeur",
    terms: "J'accepte les {terms} et j'ai lu la {privacy}.",
    termsLink: "conditions d'utilisation",
    privacyLink: "politique de confidentialité",
    termsRequired: "Vous devez accepter les conditions d'utilisation pour créer un compte.",
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
    changed: "Votre nouvelle adresse e-mail est en vigueur.",
    invalid: "Ce lien n'est pas valable ou a expiré. Connectez-vous : si votre adresse n'est pas encore confirmée, vous recevrez un nouveau lien.",
    invalidLoggedIn: "Ce lien n'est pas valable ou a expiré. Votre adresse actuelle reste en vigueur ; vous pouvez refaire la demande depuis votre profil.",
    loginLink: "Se connecter",
    profileLink: "Retour à mon profil",
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
    passwordConfirm: "Confirmez le nouveau mot de passe",
    submit: "Enregistrer le nouveau mot de passe",
    done: "Votre mot de passe est changé. Vous pouvez maintenant vous connecter.",
    invalid: "Ce lien n'est pas valable ou a expiré.",
    requestLink: "Demander un nouveau lien",
    loginLink: "Se connecter",
  },

  // Privacy page: what the site does with the data of its users, section by
  // section. Each section has a title and opening paragraphs; some add a list
  // of terms with their text, and closing paragraphs.
  privacy: {
    title: "Politique de confidentialité",
    updated: "Dernière mise à jour : 20 octobre 2026",
    sections: {
      controller: {
        title: "Qui est responsable",
        intro: [
          "MarkeTech est un projet de démonstration, sans activité commerciale : une plateforme d'offres d'emploi pour les étudiants et les jeunes diplômés en informatique, construite par Daniel Garcia pour montrer son travail. Elle fonctionne comme une vraie plateforme, mais personne n'y est engagé.",
          "Le responsable du traitement de vos données est Daniel Garcia, à Genève, en Suisse. Pour toute question sur cette page ou sur vos données, écrivez à {contact}.",
          "Le site est là pour être essayé. Vous n'avez pas besoin de vrais documents pour cela, et rien de ce que vous saisissez ne sert à autre chose qu'à faire fonctionner le site.",
        ],
      },
      data: {
        title: "Données traitées",
        intro: ["Le site n'enregistre que ce dont ses fonctions ont besoin. Selon ce que vous faites, ce sont :"],
        items: [
          { term: "Compte", text: "Adresse e-mail, mot de passe (conservé sous forme hachée, jamais lisible), prénom, nom, rôle (candidat ou employeur), état de vérification de l'adresse, dates d'inscription et de dernière connexion." },
          { term: "Profil candidat", text: "Adresse postale, numéro de téléphone, photo, CV et tout autre document que vous joignez." },
          { term: "Profil employeur", text: "Adresse postale, numéro de téléphone, photo, et l'entreprise : nom, adresse, téléphone, logo." },
          { term: "Offres d'emploi", text: "Titre, description, ville et pays, type de contrat, taux d'activité, télétravail, fourchette de salaire avec sa devise et sa période, années d'expérience demandées, date de publication ; le nom et le logo de l'entreprise sont lus sur le profil de l'employeur. Une offre publiée est visible par tous les visiteurs du site ; un brouillon ou une offre clôturée, par son employeur seulement. Une offre qui a reçu des candidatures ne peut plus être supprimée, seulement clôturée : les candidats gardent la trace de leur candidature." },
          { term: "Candidatures", text: "L'offre visée, le CV et la lettre de motivation déposés, les documents de votre profil que vous y joignez (copiés au moment de l'envoi : modifier votre profil ensuite ne change pas ce que l'employeur a reçu), la date, le statut (reçue, en cours, acceptée, refusée) et l'historique de ses changements. Une candidature est vue par le candidat et par l'employeur qui a publié l'offre ; celui-ci voit aussi vos prénom, nom, adresse e-mail, téléphone et ville, lus sur votre compte et votre profil. Vous pouvez la retirer tant que l'employeur n'a pas décidé : elle est alors supprimée avec ses fichiers." },
          { term: "Messages", text: "Échangés entre un candidat et un employeur au sujet d'une candidature : objet, texte, dates. Eux seuls peuvent les lire." },
          { term: "Favoris", text: "Les offres qu'un candidat a mises de côté." },
          { term: "Rendez-vous", text: "Proposés par un employeur au sujet d'une candidature : date et heure, description, réponse du candidat et message qui l'accompagne." },
          { term: "Avis sur la plateforme", text: "Une note globale, quatre notes de détail et un commentaire, publiés avec votre prénom et votre nom, visibles par tous les visiteurs." },
          { term: "Données techniques", text: "Le serveur enregistre les requêtes qu'il reçoit : adresse IP, page demandée, date, navigateur. Ces journaux ne servent qu'à la sécurité et au dépannage, et s'effacent automatiquement à mesure que de plus récents les remplacent." },
        ],
        outro: [
          "L'administrateur du site voit toutes ces données dans son interface d'administration, pour faire fonctionner le site et répondre à vos demandes. Rien d'autre n'est collecté : pas de profilage, pas de publicité, pas de mesure d'audience.",
        ],
      },
      cookies: {
        title: "Cookies et stockage local",
        intro: ["Le site ne pose aucun cookie tiers et n'utilise aucun traceur. Il ne garde dans votre navigateur que ce qu'il lui faut pour fonctionner :"],
        items: [
          { term: "sessionid", text: "Un cookie qui vous garde connecté ; il dure deux semaines au plus et s'efface quand vous vous déconnectez." },
          { term: "csrftoken", text: "Un cookie qui protège les formulaires contre les requêtes forgées par un autre site ; il dure un an." },
          { term: "marketech.locale", text: "La langue que vous avez choisie, gardée dans le stockage local de votre navigateur jusqu'à ce que vous l'effaciez." },
        ],
      },
      emails: {
        title: "E-mails",
        intro: ["Le site ne vous écrit qu'au sujet de votre compte : pour vérifier votre adresse à l'inscription, et pour vous envoyer un lien si vous oubliez votre mot de passe. Pas de lettre d'information, pas de publicité. Les e-mails partent par le service de messagerie d'Infomaniak."],
      },
      hosting: {
        title: "Hébergement et partage",
        intro: [
          "Le site tourne sur un serveur loué chez Infomaniak, en Suisse, et ses données restent en Suisse. Infomaniak héberge le serveur, conserve ses copies de sauvegarde et envoie ses e-mails ; c'est la seule entreprise qui manipule des données pour le compte du site.",
          "Le code source du site est public sur GitHub et ne contient aucune donnée personnelle. Aucune donnée n'est vendue, louée ni transmise à qui que ce soit d'autre. Dans le site, vos données ne sont montrées qu'aux personnes que ses fonctions impliquent : un employeur voit les candidatures à ses offres, un candidat voit l'entreprise derrière une offre, et les avis sont publics.",
        ],
      },
      retention: {
        title: "Durée de conservation",
        intro: [
          "Vos données sont conservées tant que votre compte existe. Ce que vous supprimez vous-même, une offre, une candidature retirée, un favori, un document, disparaît aussitôt, fichiers compris. Quand votre compte est supprimé, tout ce qui s'y rattache part avec lui : profil, offres, candidatures, messages, rendez-vous, favoris et avis.",
          "Pour faire supprimer votre compte, écrivez à {contact} depuis l'adresse du compte. Les journaux du serveur s'effacent automatiquement, comme dit plus haut.",
        ],
      },
      security: {
        title: "Sécurité",
        intro: ["Tout le site est servi en HTTPS. Les mots de passe sont conservés hachés, jamais en clair. Les photos et les documents que vous déposez (CV, lettres, autres documents) sont privés : le site vérifie qui les demande avant de les remettre, et aucune adresse n'y mène directement ; seul le logo de l'entreprise est public, puisqu'il accompagne les offres. L'accès au serveur lui-même est réservé à son administrateur."],
      },
      rights: {
        title: "Vos droits",
        intro: [
          "En vertu de la loi fédérale sur la protection des données (LPD), vous pouvez demander quelles données le site détient sur vous, les faire corriger ou supprimer, et vous opposer à leur traitement. Un message à {contact} suffit : la réponse est gratuite et arrive, en règle générale, dans les 30 jours. Vous pouvez aussi modifier la plupart de vos données vous-même, depuis votre compte.",
          "Si vous estimez que vos droits ne sont pas respectés, vous pouvez vous adresser au Préposé fédéral à la protection des données et à la transparence (PFPDT).",
        ],
      },
      changes: {
        title: "Modifications de cette page",
        intro: ["Cette page décrit le site tel qu'il est. Elle change quand le site change, et la date en tête dit quand elle a été mise à jour pour la dernière fois."],
      },
    },
  },

  // Terms of use, accepted at sign-up: sections in the same shape as the
  // privacy page (title and paragraphs)
  terms: {
    title: "Conditions d'utilisation",
    updated: "Dernière mise à jour : 20 octobre 2026",
    sections: {
      purpose: {
        title: "Ce qu'est MarkeTech",
        intro: [
          "MarkeTech est un projet de démonstration réalisé par Daniel Garcia, à Genève, pour montrer son travail : une plateforme d'offres d'emploi pour les étudiants et les jeunes diplômés en informatique. Il n'a aucune activité commerciale : aucune offre n'engage qui que ce soit, personne n'est recruté par son intermédiaire, et rien n'y est vendu.",
          "En créant un compte, vous acceptez les présentes conditions. Si vous ne les acceptez pas, n'utilisez pas le site.",
        ],
      },
      account: {
        title: "Votre compte",
        intro: [
          "Un compte est personnel : une personne, une adresse e-mail qui vous appartient, un mot de passe que vous gardez pour vous. Vous choisissez votre rôle à l'inscription, candidat ou employeur, et vous répondez de ce qui est fait avec votre compte.",
          "Vous pouvez demander la suppression de votre compte à tout moment, en écrivant à {contact} depuis l'adresse du compte ; tout ce qui s'y rattache est supprimé avec lui.",
        ],
      },
      use: {
        title: "Usage du site",
        intro: [
          "Le site est là pour être essayé. Vous n'avez pas besoin d'y mettre de vrais documents ni de vraies données, et vous n'y mettez pas les données d'une autre personne sans son accord.",
          "Il est interdit d'y publier un contenu illicite, trompeur ou offensant, de se faire passer pour quelqu'un d'autre, de tenter d'accéder à un compte ou à des données qui ne sont pas les vôtres, ou de perturber le fonctionnement du site, par exemple par des requêtes automatisées.",
        ],
      },
      content: {
        title: "Ce que vous publiez",
        intro: [
          "Ce que vous publiez (profil, offres, documents) reste à vous, et vous en répondez : un employeur est responsable des offres qu'il publie. En le publiant, vous autorisez le site à le montrer aux personnes que ses fonctions impliquent, et à tout visiteur pour une offre publiée.",
          "L'administrateur du site peut retirer un contenu contraire aux présentes conditions, et suspendre ou supprimer le compte qui l'a publié, sans préavis.",
        ],
      },
      availability: {
        title: "Sans garantie",
        intro: [
          "Le site est fourni tel quel, sans garantie de disponibilité ni d'exactitude : il peut changer, être interrompu ou s'arrêter à tout moment, sans préavis. Dans les limites de la loi, son auteur ne répond pas d'un dommage lié à son usage ou à son indisponibilité.",
        ],
      },
      data: {
        title: "Vos données",
        intro: [
          "Ce que le site fait de vos données est décrit dans la politique de confidentialité, accessible depuis le pied de page. Vous en prenez connaissance en créant un compte.",
        ],
      },
      law: {
        title: "Droit applicable",
        intro: [
          "Les présentes conditions sont soumises au droit suisse. Le for est à Genève, sous réserve des dispositions impératives.",
        ],
      },
      changes: {
        title: "Modifications de ces conditions",
        intro: [
          "Ces conditions peuvent changer avec le site ; la date en tête dit quand elles ont été mises à jour pour la dernière fois. En continuant d'utiliser le site après une modification, vous l'acceptez.",
        ],
      },
    },
  },

  // Profile page: names and contact details, company, files and documents,
  // then the account: e-mail address and password
  profile: {
    title: "Mon profil",
    identity: "Identité",
    firstName: "Prénom",
    lastName: "Nom",
    contact: "Coordonnées",
    phone: "Téléphone",
    address: "Adresse",
    postalCode: "Code postal",
    city: "Ville",
    country: "Pays",
    noCountry: "Non renseigné",
    company: "Entreprise",
    companyName: "Nom de l'entreprise",
    companyAddress: "Adresse",
    companyPostalCode: "Code postal",
    companyCity: "Ville",
    companyCountry: "Pays",
    companyPhone: "Téléphone",
    save: "Enregistrer",
    saved: "Enregistré.",
    photo: "Photo",
    logo: "Logo",
    files: "Documents",
    cv: "CV",
    documents: "Autres documents",
    noFile: "Aucun fichier pour l'instant.",
    choose: "Choisir un fichier",
    replace: "Remplacer",
    remove: "Retirer",
    add: "Ajouter un document",
    sending: "Envoi…",
    fileSaved: "Fichier enregistré.",
    fileRemoved: "Fichier retiré.",
    rules: "{types} · {size} Mo au plus",
    limit: "Vous avez atteint la limite de {max} documents.",
    confirmRemove: "Retirer ce fichier ?",
    addedOn: "ajouté le {date}",
    loadFailed: "Votre profil ne peut pas être chargé. Veuillez réessayer plus tard.",
    tooBig: "Ce fichier dépasse {size} Mo.",
    wrongType: "Ce type de fichier n'est pas accepté ({types}).",
    account: "Compte",
    email: "Adresse e-mail",
    currentEmail: "Adresse actuelle : {email}",
    newEmail: "Nouvelle adresse e-mail",
    changeEmail: "Changer d'adresse",
    emailSent: "E-mail envoyé. Ouvrez-le et suivez son lien : votre adresse actuelle reste en vigueur jusque-là.",
    emailPending: "Confirmation en attente pour {email}.",
    cancel: "Annuler",
    password: "Mot de passe",
    currentPassword: "Mot de passe actuel",
    newPassword: "Nouveau mot de passe",
    newPasswordConfirm: "Confirmez le nouveau mot de passe",
    changePassword: "Changer de mot de passe",
    passwordChanged: "Mot de passe changé.",
  },

  // Job offers: the public list, its filters, and the detail of an offer
  offers: {
    title: "Offres d'emploi",
    count: "Aucune offre | {count} offre | {count} offres",
    filters: "Filtres",
    search: "Rechercher",
    reset: "Réinitialiser",
    keyword: "Mot-clé",
    keywordHint: "Dans le titre",
    city: "Ville",
    country: "Pays",
    anyCountry: "Tous les pays",
    contractLabel: "Contrat",
    anyContract: "Tous les contrats",
    remoteLabel: "Télétravail",
    anyRemote: "Indifférent",
    salaryMin: "Salaire minimum",
    publishedAfter: "Publiée depuis le",
    none: "Aucune offre ne correspond à ces critères.",
    loadFailed: "Les offres n'ont pas pu être chargées.",
    page: "Page {page} sur {pages}",
    previous: "Précédent",
    next: "Suivant",
    publishedOn: "Publiée le {date}",
    detailsLink: "Voir l'offre",
    back: "Toutes les offres",
    notFound: "Cette offre n'existe pas, ou n'est plus publiée.",
    // Applying, under the heading of an offer
    apply: "Postuler",
    loginToApply: "{login} pour postuler à cette offre.",
    loginLink: "Connectez-vous",
    applied: "Vous avez postulé le {date}",
    myApplicationsLink: "Mes candidatures",
    description: "Le poste",
    facts: "En bref",
    place: "Lieu",
    salaryLabel: "Salaire",
    currencyLabel: "Devise",
    periodLabel: "Période",
    experienceLabel: "Expérience",
    contract: {
      permanent: "CDI",
      fixed_term: "CDD",
      internship: "Stage",
      student: "Job étudiant",
    },
    remote: {
      on_site: "Sur site",
      hybrid: "Hybride",
      remote: "À distance",
    },
    period: {
      month: "par mois",
      year: "par an",
    },
    salary: {
      range: "{currency} {range} {period}",
      from: "Dès {currency} {amount} {period}",
      upTo: "Jusqu'à {currency} {amount} {period}",
    },
    status: {
      draft: "Brouillon",
      published: "Publiée",
      closed: "Clôturée",
    },
    experience: "{count} an d'expérience | {count} ans d'expérience",
  },

  // The offers of an employer: the list with its moves
  myOffers: {
    title: "Mes offres",
    new: "Nouvelle offre",
    none: "Vous n'avez pas encore d'offre. Créez la première : elle reste un brouillon tant que vous ne la publiez pas.",
    loadFailed: "Vos offres n'ont pas pu être chargées.",
    edit: "Modifier",
    publish: "Publier",
    republish: "Republier",
    close: "Clôturer",
    delete: "Supprimer",
    confirmDelete: "Supprimer l'offre « {title} » ? Elle ne pourra pas être récupérée.",
    needsCompany: "Indiquez le nom de votre entreprise dans votre profil avant de publier.",
    companyLink: "Compléter mon profil",
    applications: "Aucune candidature | {count} candidature | {count} candidatures",
  },

  // The form of an offer, new or changed
  offerForm: {
    newTitle: "Nouvelle offre",
    editTitle: "Modifier l'offre",
    back: "Mes offres",
    notFound: "Cette offre n'existe pas, ou n'est pas la vôtre.",
    title: "Titre",
    description: "Description",
    descriptionHint: "Le poste, l'équipe, le profil recherché. Les sauts de ligne sont conservés.",
    city: "Ville",
    country: "Pays",
    chooseCountry: "Choisir un pays",
    contract: "Contrat",
    chooseContract: "Choisir un contrat",
    remote: "Télétravail",
    workload: "Taux d'activité (%)",
    workloadMax: "Taux maximum",
    workloadHint: "Du premier chiffre au second ; le même chiffre dans les deux pour un taux fixe.",
    experience: "Années d'expérience demandées",
    salary: "Salaire brut",
    salaryMax: "Salaire maximum",
    salaryHint: "Minimum et maximum, ou un seul des deux ; les deux vides pour ne rien dire.",
    required: "Ce champ est obligatoire.",
    save: "Enregistrer",
    saveAndPublish: "Enregistrer et publier",
    saveAndRepublish: "Enregistrer et republier",
  },

  // Job applications: what the candidate's and the employer's pages share
  applications: {
    status: {
      received: "Reçue",
      in_progress: "En cours",
      accepted: "Acceptée",
      rejected: "Refusée",
    },
    // One step of the history: "En cours le 14 octobre"
    historyStep: "{status} le {date}",
    sentOn: "Envoyée le {date}",
    cv: "CV",
    coverLetter: "Lettre de motivation",
  },

  // Applying to an offer: the form of a candidate
  apply: {
    title: "Postuler",
    back: "Retour à l'offre",
    notOpen: "Cette offre n'est pas ouverte aux candidatures.",
    alreadyApplied: "Vous avez déjà postulé à cette offre.",
    myApplicationsLink: "Voir mes candidatures",
    cv: "CV",
    cvProfile: "Le CV de mon profil ({name})",
    cvOther: "Un autre fichier",
    cvNone: "Votre profil n'a pas encore de CV : envoyez-en un ici, ou gardez-en un dans votre profil pour le joindre d'un clic.",
    cvRequired: "Choisissez un CV.",
    coverLetter: "Lettre de motivation (facultatif)",
    choose: "Choisir un fichier",
    replace: "Remplacer",
    remove: "Enlever",
    documents: "Documents de mon profil à joindre",
    documentsNone: "Votre profil n'a pas de document.",
    profileLink: "En ajouter",
    fileHint: "{types}, {size} Mo au plus.",
    tooBig: "Ce fichier dépasse {size} Mo.",
    wrongType: "Ce type de fichier n'est pas accepté ({types}).",
    submit: "Envoyer ma candidature",
  },

  // The applications of a candidate: the list with the withdrawal
  myApplications: {
    title: "Mes candidatures",
    none: "Vous n'avez pas encore postulé. Les offres sont sur l'accueil.",
    loadFailed: "Vos candidatures n'ont pas pu être chargées.",
    offerLink: "Voir l'offre",
    offerClosed: "offre clôturée",
    withdraw: "Retirer",
    confirmWithdraw: "Retirer votre candidature à « {title} » ? Ses fichiers seront supprimés.",
  },

  // The applications to one offer, for its employer
  offerApplications: {
    title: "Candidatures",
    back: "Mes offres",
    notFound: "Cette offre n'existe pas, ou n'est pas la vôtre.",
    loadFailed: "Les candidatures n'ont pas pu être chargées.",
    count: "Aucune candidature pour l'instant | {count} candidature | {count} candidatures",
    set: {
      in_progress: "Mettre en cours",
      accepted: "Accepter",
      rejected: "Refuser",
    },
    confirm: {
      accepted: "Accepter la candidature de {name} ?",
      rejected: "Refuser la candidature de {name} ?",
    },
  },

  // Not-found page, for any address the router does not know
  notFound: {
    title: "Page introuvable",
    text: "Il n'y a rien à cette adresse. Elle a peut-être été mal saisie, ou la page a changé de place.",
    homeLink: "Retour à l'accueil",
  },

  // Confirmation dialog, the question being given by the page
  dialog: {
    cancel: "Annuler",
  },

  // Messages shared by every form
  form: {
    failed: "Une erreur est survenue. Veuillez réessayer.",
    unreachable: "Le serveur est injoignable. Veuillez réessayer plus tard.",
    tooMany: "Trop de tentatives. Patientez un instant avant de réessayer.",
    passwordMismatch: "Les deux mots de passe ne correspondent pas.",
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
