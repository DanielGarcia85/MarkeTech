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
    notice: "Site de démonstration",
  },

  // The two roles, as shown to the logged-in user (header menu, profile)
  roles: {
    candidate: "Candidat",
    employer: "Employeur",
  },

  // Header: session state and links of the account
  header: {
    demo: "Essayer la démo",
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
    myFavorites: "Mes favoris",
    receivedApplications: "Candidatures reçues",
    account: "Mon compte",
    profile: "Profil",
    credentials: "Identifiants",
    messaging: "Messagerie",
    openConversations: "Ouvertes",
    closedConversations: "Closes",
    appointments: "Rendez-vous",
    platform: "Plateforme",
    allReviews: "Tous les avis",
    myReview: "Mon avis",
  },

  // Empty lists: the way to the place where they get filled
  empty: {
    browse: "Voir les offres",
  },

  // Public demonstration: the demo accounts of the login page
  demo: {
    title: "Essayer la démo",
    text: "Découvrez le site sans créer de compte, avec un compte de démonstration partagé et remis à zéro chaque nuit.",
    terms: "En essayant la démo, vous acceptez les {terms} et avez lu la {privacy}.",
    candidate: "Candidat·e",
    employer: "Employeur",
    unavailable: "La démo n'est pas disponible pour l'instant.",
    band: "Compte de démo, remis à zéro chaque nuit.",
    locked: "Compte de démo : l'adresse e-mail et le mot de passe ne sont pas modifiables.",
  },

  // Footer: who is behind the site, where to find more, how to get in touch
  // (the technologies come from "about": in their list, a non-breaking
  // space glues each dot to the name before it, so that a line never
  // starts with a dot nor splits a name)
  footer: {
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
    invalidLoggedIn: "Ce lien n'est pas valable ou a expiré. Votre adresse actuelle reste en vigueur ; vous pouvez refaire la demande depuis vos identifiants.",
    loginLink: "Se connecter",
    credentialsLink: "Retour à mes identifiants",
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
    updated: "Dernière mise à jour : 29 octobre 2026",
    sections: {
      summary: {
        title: "En bref",
        intro: [
          "MarkeTech est un projet de démonstration sans activité commerciale, exploité par Daniel Garcia à Genève.",
          "Le site n'enregistre que ce dont ses fonctions ont besoin et ne s'en sert à rien d'autre : pas de publicité, pas de traceur, pas de mesure d'audience, pas de profilage.",
          "Tout est hébergé en Suisse, chez Infomaniak. Aucune donnée n'est vendue ni transmise.",
          "Seules les offres publiées et les avis sont publics. Vos documents ne sont vus que par les employeurs auxquels vous postulez.",
          "Vous pouvez consulter, corriger et faire supprimer vos données à tout moment, en écrivant à {contact}.",
        ],
      },
      controller: {
        title: "Qui est responsable",
        intro: [
          "MarkeTech est une plateforme d'offres d'emploi pour les étudiants et les jeunes diplômés en informatique, construite par Daniel Garcia pour montrer son travail. Elle fonctionne comme une vraie plateforme, mais personne n'y est engagé.",
          "Le responsable du traitement de vos données est Daniel Garcia, personne privée, à Genève, en Suisse. Pour toute question sur cette page ou sur vos données, écrivez à {contact}.",
          "Le site est là pour être essayé. Vous n'avez pas besoin de vrais documents pour cela, et rien de ce que vous saisissez ne sert à autre chose qu'à faire fonctionner le site.",
        ],
      },
      data: {
        title: "Données traitées et finalités",
        intro: ["Le site n'enregistre que ce dont ses fonctions ont besoin. Selon ce que vous faites, ce sont :"],
        items: [
          { term: "Compte", text: "Adresse e-mail, mot de passe (conservé sous forme hachée, jamais lisible), prénom, nom, rôle (candidat ou employeur), état de vérification de l'adresse, dates d'inscription et de dernière connexion, date d'acceptation des conditions d'utilisation, langue de l'interface (relevée à la connexion et quand vous en changez) et choix de recevoir ou non les e-mails de notification. Finalité : vous identifier et vous écrire." },
          { term: "Profil candidat", text: "Adresse postale, numéro de téléphone, photo, CV et tout autre document que vous joignez. Finalité : postuler sans tout saisir à nouveau." },
          { term: "Profil employeur", text: "Adresse postale, numéro de téléphone, photo, et l'entreprise : nom, adresse, téléphone, logo. Seuls le nom et le logo de l'entreprise sont publics, avec les offres ; vos propres coordonnées et votre photo restent privées." },
          { term: "Offres d'emploi", text: "Titre, description, ville et pays, type de contrat, taux d'activité, télétravail, fourchette de salaire avec sa devise et sa période, années d'expérience demandées, date de publication ; le nom et le logo de l'entreprise sont lus sur le profil de l'employeur. Une offre publiée est visible par tous les visiteurs du site ; un brouillon ou une offre clôturée, par son employeur seulement. Une offre publiée doit être clôturée avant de pouvoir être supprimée, et une offre qui a reçu des candidatures ne peut plus qu'être clôturée, pour que les candidats gardent la trace de leur candidature." },
          { term: "Candidatures", text: "L'offre visée, le CV et la lettre de motivation déposés, les documents de votre profil que vous y joignez (copiés au moment de l'envoi : modifier votre profil ensuite ne change pas ce que l'employeur a reçu), la date, le statut (reçue, en cours, acceptée, refusée), l'historique de ses changements et le moment où chacun a été vu. Une candidature est vue par le candidat et par l'employeur qui a publié l'offre ; celui-ci voit aussi vos prénom, nom, adresse e-mail, téléphone et ville, jamais votre adresse postale ni votre photo. Vous pouvez la retirer tant que l'employeur n'a pas décidé : elle est alors supprimée avec ses fichiers." },
          { term: "Messages", text: "Échangés entre un candidat et l'employeur de l'offre au sujet d'une candidature : le texte, la date d'envoi et celle de la lecture par l'autre. La conversation s'ouvre quand l'employeur met la candidature en cours ; elle reste lisible, sans plus pouvoir écrire, une fois la candidature acceptée ou refusée. Les deux participants peuvent la lire, personne d'autre. Elle est supprimée avec la candidature." },
          { term: "Rendez-vous", text: "Proposés par un employeur au sujet d'une candidature en cours : date, heure et durée, lieu, précisions éventuelles ; puis la réponse du candidat et son message, ou l'annulation par l'employeur et son message éventuel. Vus par les deux participants seulement ; chacun peut les exporter vers un agenda (fichier .ics), avec l'offre, l'autre participant, le lieu et les précisions." },
          { term: "Favoris", text: "Les offres qu'un candidat a mises de côté, avec la date. Lui seul les voit ; l'employeur d'une offre sait combien de candidats l'ont mise de côté, jamais lesquels." },
          { term: "Avis sur la plateforme", text: "Une note globale, quatre notes de détail et un commentaire, publiés avec votre prénom, l'initiale de votre nom et votre rôle (pour un employeur, le nom de son entreprise), visibles par tous les visiteurs. Un avis par compte, que vous pouvez modifier ou supprimer à tout moment ; les comptes de démonstration ne peuvent pas en publier." },
          { term: "Avis de sécurité", text: "Quand l'adresse e-mail ou le mot de passe de votre compte change, le site vous écrit (à l'ancienne adresse pour un changement d'adresse) en indiquant l'adresse IP, le navigateur et l'heure de la demande, pour que vous repériez un changement que vous n'avez pas fait. L'adresse IP n'est écrite que dans cet e-mail ; le site ne l'enregistre nulle part." },
          { term: "Modération", text: "Chaque avis écrit ou modifié, et chaque offre publiée ou modifiée alors qu'elle est publiée, est envoyé par e-mail à l'administrateur, avec son texte, le nom et l'adresse e-mail de son auteur, pour qu'un contenu illicite puisse être retiré rapidement." },
          { term: "Protection contre les abus", text: "Pour freiner les attaques contre la connexion et l'inscription, le site compte les tentatives par adresse IP et par adresse e-mail, en mémoire seulement, pendant quelques minutes. Il limite aussi le nombre de modifications que chaque compte peut faire par heure." },
          { term: "Données techniques", text: "Les serveurs tiennent des journaux techniques (requêtes reçues, avec l'adresse IP, la date, la page et le navigateur) pour la sécurité et le dépannage seulement." },
          { term: "Mises à jour en direct", text: "Tant que vous êtes connecté, chaque onglet ouvert garde une connexion (WebSocket) avec le serveur, authentifiée par votre cookie de session, pour que les nouveaux messages et les nouvelles apparaissent sans recharger la page. Elle ne transporte que des signaux sans contenu, et n'enregistre rien." },
        ],
        outro: [
          "L'administrateur du site voit ces données dans son interface d'administration, pour faire fonctionner le site et répondre à vos demandes.",
          "Les deux comptes de démonstration sont partagés par tous les visiteurs : ce que vous y écrivez ou y déposez est vu par les suivants, jusqu'à leur remise à zéro chaque nuit. N'y mettez rien de personnel.",
        ],
      },
      bases: {
        title: "Sur quelle base",
        intro: [
          "En droit suisse, le site traite vos données dans le respect des principes de la loi fédérale sur la protection des données (LPD). Pour les visiteurs de l'Union européenne, auxquels le règlement général sur la protection des données (RGPD) peut s'appliquer, les bases sont :",
        ],
        items: [
          { term: "Exécution du service (RGPD, art. 6, par. 1, let. b)", text: "Votre compte, votre profil, les offres, les candidatures, les messages, les rendez-vous, les favoris, les avis, et les e-mails qui s'y rapportent : ce que vous demandez au site de faire." },
          { term: "Intérêt légitime (RGPD, art. 6, par. 1, let. f)", text: "La sécurité du site et de votre compte (journaux, limites contre les abus, avis de sécurité), la modération des contenus publics et les sauvegardes. L'intérêt est de garder le site sûr et conforme au droit ; vous pouvez vous y opposer (voir « Vos droits »)." },
        ],
      },
      recipients: {
        title: "Qui reçoit vos données",
        intro: ["Vos données ne sont montrées ou transmises qu'à :"],
        items: [
          { term: "Les autres utilisateurs", text: "Dans la mesure où les fonctions l'impliquent : un employeur voit les candidatures à ses offres, un candidat voit l'entreprise derrière une offre, les participants d'une conversation ou d'un rendez-vous voient ce qui le concerne." },
          { term: "Le public", text: "Les offres publiées (avec le nom et le logo de l'entreprise) et les avis (prénom, initiale du nom, rôle, entreprise)." },
          { term: "Infomaniak", text: "Infomaniak Network SA, à Genève, héberge le serveur, conserve ses sauvegardes chiffrées et envoie ses e-mails, pour le compte du site et en Suisse." },
          { term: "Autres services", text: "GitHub héberge le code source public et les images de l'application, et Healthchecks.io surveille que la sauvegarde de la nuit a eu lieu : aucun des deux ne reçoit de données des utilisateurs." },
        ],
        outro: ["Aucune donnée n'est vendue, louée ni transmise à qui que ce soit d'autre."],
      },
      abroad: {
        title: "Données à l'étranger",
        intro: [
          "Vos données restent en Suisse et ne sont communiquées à aucun autre pays. Les e-mails envoyés à votre propre adresse vont, bien sûr, chez le fournisseur de messagerie que vous avez choisi.",
        ],
      },
      retention: {
        title: "Durée de conservation",
        intro: ["Vos données ne sont conservées que le temps nécessaire :"],
        items: [
          { term: "Compte et contenus", text: "Tant que votre compte existe. Ce que vous supprimez vous-même (un document, une photo, un favori, un avis, une candidature retirée, une offre qui peut être supprimée) disparaît aussitôt du site, fichiers compris. Quand un compte est supprimé, tout ce qui s'y rattache part avec lui ; pour un employeur, les candidatures à ses offres aussi." },
          { term: "Sauvegardes", text: "Une donnée supprimée du site subsiste un temps dans les sauvegardes chiffrées, qui s'effacent automatiquement au plus tard après six mois." },
          { term: "Journaux techniques", text: "Effacés automatiquement : le serveur n'en garde qu'un volume limité, les plus anciennes lignes étant remplacées par les plus récentes." },
          { term: "E-mails de modération", text: "Supprimés une fois traités." },
          { term: "Comptes de démonstration", text: "Remis à zéro chaque nuit, avec tout ce qui y a été fait." },
        ],
        outro: ["Pour faire supprimer votre compte, écrivez à {contact} depuis l'adresse du compte."],
      },
      cookies: {
        title: "Cookies et stockage local",
        intro: [
          "Le site ne pose aucun cookie tiers, n'utilise aucun traceur et n'affiche aucune publicité. Il ne garde dans votre navigateur que ce qu'il lui faut pour fonctionner, et c'est pourquoi il ne demande aucun consentement :",
        ],
        items: [
          { term: "sessionid", text: "Un cookie qui vous garde connecté ; il dure deux semaines au plus et s'efface quand vous vous déconnectez. Envoyé en HTTPS seulement, et hors de portée des scripts de la page." },
          { term: "csrftoken", text: "Un cookie qui protège les formulaires contre les requêtes forgées par un autre site ; il dure un an. Envoyé en HTTPS seulement." },
          { term: "marketech.locale", text: "La langue que vous avez choisie, gardée dans le stockage local de votre navigateur jusqu'à ce que vous l'effaciez." },
        ],
        outro: [
          "Vous pouvez les effacer ou les bloquer dans votre navigateur : le site oublie alors votre langue, et vous ne pouvez plus vous connecter. La police du site est servie par le site lui-même, sans aucune requête vers Google ou un autre fournisseur.",
        ],
      },
      security: {
        title: "Sécurité",
        intro: [
          "Tout le site est servi en HTTPS. Les mots de passe sont conservés hachés, jamais en clair. Les photos et les documents que vous déposez sont privés : le site vérifie qui les demande avant de les remettre, et aucune adresse n'y mène directement. Les documents d'une candidature sont vus par le candidat et par l'employeur de l'offre ; seul le logo de l'entreprise est public, puisqu'il accompagne les offres. La base de données n'est pas joignable depuis Internet, les sauvegardes sont chiffrées, et l'accès au serveur est réservé à son administrateur.",
          "Si une violation de la sécurité faisait courir un risque élevé à vos données, le site en informerait le Préposé fédéral à la protection des données et à la transparence (PFPDT) et, lorsque votre protection l'exige, vous préviendrait directement par e-mail.",
        ],
      },
      rights: {
        title: "Vos droits",
        intro: [
          "Vous pouvez demander quelles données le site détient sur vous et en recevoir une copie, aussi dans un format électronique courant pour les emporter ailleurs ; les faire corriger ; les faire supprimer ; et vous opposer à un traitement fondé sur un intérêt légitime. Écrivez à {contact}, depuis l'adresse de votre compte si vous en avez un : la réponse est gratuite et arrive dans les 30 jours. Vous pouvez aussi modifier vous-même la plupart de vos données, depuis votre compte.",
          "Si vous estimez que vos droits ne sont pas respectés, vous pouvez vous adresser au Préposé fédéral à la protection des données et à la transparence (PFPDT, www.edoeb.admin.ch). Si vous habitez dans l'Union européenne, vous pouvez aussi vous adresser à l'autorité de protection des données de votre pays, par exemple la CNIL en France.",
        ],
      },
      automated: {
        title: "Aucune décision automatisée",
        intro: [
          "Aucune décision n'est prise par une machine : le site ne trie, ne note ni ne filtre les candidats ; les employeurs lisent eux-mêmes les candidatures.",
          "Ne mettez aucune donnée sensible dans vos documents (santé, religion, opinions politiques, copie d'une pièce d'identité, numéro AVS) : le site n'en a pas besoin.",
        ],
      },
      changes: {
        title: "Modifications de cette page",
        intro: [
          "Cette page décrit le site tel qu'il est. Elle change quand le site change, et la date en tête dit quand elle a été mise à jour pour la dernière fois. Une modification importante est annoncée par e-mail aux comptes.",
        ],
      },
    },
  },

  // Terms of use, accepted at sign-up: sections in the same shape as the
  // privacy page (title and paragraphs)
  terms: {
    title: "Conditions d'utilisation",
    updated: "Dernière mise à jour : 29 octobre 2026",
    sections: {
      essentials: {
        title: "Points importants",
        intro: [
          "MarkeTech est un projet de démonstration : gratuit, sans activité commerciale, et personne n'y est recruté. Les offres qui y sont publiées sont des exemples.",
          "Les deux comptes de démonstration sont publics et remis à zéro chaque nuit : n'y mettez jamais de données réelles ou personnelles.",
          "Ce que vous publiez est en ligne aussitôt ; l'administrateur le lit ensuite et peut le retirer ou bloquer le compte.",
          "Le site est fourni sans garantie et peut s'arrêter ; son auteur ne répond que des dommages causés intentionnellement ou par négligence grave.",
          "Ces conditions peuvent changer ; une modification importante est annoncée par e-mail 14 jours à l'avance.",
        ],
      },
      purpose: {
        title: "Ce qu'est MarkeTech",
        intro: [
          "MarkeTech est un projet de démonstration réalisé par Daniel Garcia, à Genève, pour montrer son travail : une plateforme d'offres d'emploi pour les étudiants et les jeunes diplômés en informatique. Il n'a aucune activité commerciale : aucune offre n'engage qui que ce soit, personne n'est recruté par son intermédiaire, et rien n'y est vendu.",
          "MarkeTech n'est pas une agence de placement : il ne sélectionne pas les candidats, ne prend aucune part à la conclusion d'un contrat de travail et ne reçoit de rémunération de personne.",
          "Les offres du site sont des exemples faits pour l'essayer. N'y publiez pas un vrai poste en attendant de vraies candidatures.",
        ],
      },
      acceptance: {
        title: "Acceptation",
        intro: [
          "Vous acceptez les présentes conditions en cochant la case du formulaire d'inscription quand vous créez un compte, ou celle de la page de connexion quand vous ouvrez un compte de démonstration. Si vous ne les acceptez pas, n'utilisez pas le site.",
        ],
      },
      account: {
        title: "Votre compte",
        intro: [
          "Le site est ouvert aux personnes de 18 ans révolus. Un compte est personnel : une personne, une adresse e-mail qui vous appartient, un mot de passe que vous gardez pour vous. Vous choisissez votre rôle à l'inscription, candidat ou employeur, et vous répondez de ce qui est fait avec votre compte.",
          "Deux comptes de démonstration, une candidate et un employeur, s'ouvrent sans mot de passe depuis la page de connexion. Ils sont partagés par tous les visiteurs, leur adresse et leur mot de passe ne se changent pas, et ils sont remis à zéro chaque nuit : tout ce qui y a été fait disparaît, y compris ce qui relie votre propre compte à eux (une candidature à une de leurs offres, ses messages, vos favoris sur ces offres). Votre compte lui-même et ce qui ne dépend que de lui restent.",
        ],
      },
      use: {
        title: "Usage du site",
        intro: [
          "Le site est là pour être essayé. Vous n'avez pas besoin d'y mettre de vrais documents ni de vraies données, et vous n'y mettez pas les données d'une autre personne sans son accord.",
          "Il est interdit de se faire passer pour quelqu'un d'autre, de tenter d'accéder à un compte ou à des données qui ne sont pas les vôtres, de copier le contenu du site par des moyens automatisés ou d'en perturber le fonctionnement. Pour protéger le site, chaque compte peut faire jusqu'à 300 modifications par heure (60 pour un compte de démonstration), et les tentatives de connexion et d'inscription sont limitées.",
        ],
      },
      offers: {
        title: "Offres",
        intro: [
          "Un employeur répond des offres qu'il publie. Une offre décrit un seul poste, avec loyauté ; elle n'opère aucune discrimination fondée sur le sexe, l'origine, la nationalité, l'âge, la religion, le handicap ou l'orientation sexuelle, et ne demande aucun paiement aux candidats. N'utilisez qu'un logo et des images que vous avez le droit d'utiliser.",
          "Une offre publiée doit être clôturée avant de pouvoir être supprimée ; une offre qui a reçu des candidatures ne peut plus qu'être clôturée.",
        ],
      },
      exchanges: {
        title: "Candidatures, messages, rendez-vous et avis",
        intro: [
          "Un candidat peut retirer sa candidature tant que l'employeur n'a pas décidé. Ne mettez dans vos documents ni copie d'une pièce d'identité, ni numéro AVS, ni données de santé.",
          "Les messages et les rendez-vous ne portent que sur la candidature, et restent courtois.",
          "Un avis porte sur la plateforme : honnête, sans injure, sans nommer d'autre personne. Un avis par compte ; les comptes de démonstration ne peuvent pas en publier.",
        ],
      },
      prohibited: {
        title: "Contenus interdits et signalement",
        intro: [
          "Il est interdit de publier un contenu illicite, en particulier un contenu qui porte atteinte à l'honneur ou à la personnalité de quelqu'un, incite à la discrimination ou à la haine, ou viole un droit d'auteur ; un contenu trompeur, du spam ou de la publicité ; et les données personnelles d'une autre personne sans son accord.",
          "Pour signaler un contenu, écrivez à {contact} en indiquant où il se trouve : le signalement est examiné rapidement.",
        ],
      },
      moderation: {
        title: "Modération",
        intro: [
          "Ce que vous publiez est en ligne aussitôt ; l'administrateur en est averti et le lit ensuite. Il peut retirer un contenu contraire aux présentes conditions ou à la loi, et bloquer un compte : ses offres et son avis sont alors masqués, rien n'est supprimé, et le blocage peut être levé. Sauf urgence, il prévient la personne concernée et lui en donne le motif.",
        ],
      },
      licence: {
        title: "Ce que vous publiez",
        intro: [
          "Ce que vous publiez (profil, offres, documents, messages, avis) reste à vous. Vous autorisez le site, gratuitement et aussi longtemps qu'il reste en ligne, à le conserver et à le montrer aux personnes que ses fonctions impliquent, et à tout visiteur pour une offre publiée ou un avis, pour le seul fonctionnement du site. Vous garantissez en détenir les droits.",
        ],
      },
      end: {
        title: "Fin de l'utilisation",
        intro: [
          "Vous pouvez cesser d'utiliser le site à tout moment et faire supprimer votre compte en écrivant à {contact} depuis l'adresse du compte ; tout ce qui s'y rattache est supprimé avec lui, comme le décrit la politique de confidentialité.",
          "Un compte qui enfreint les présentes conditions peut être bloqué ou supprimé. Si le site devait s'arrêter définitivement, les comptes en seraient avertis par e-mail 30 jours à l'avance, pour que chacun puisse récupérer ses documents.",
        ],
      },
      availability: {
        title: "Sans garantie",
        intro: [
          "Le site est fourni gratuitement, tel quel, sans garantie de disponibilité, de continuité ni d'exactitude des offres, ni qu'une candidature reçoive une réponse : il peut changer ou être interrompu à tout moment. Gardez votre propre copie de vos documents.",
        ],
      },
      liability: {
        title: "Responsabilité",
        intro: [
          "Daniel Garcia répond des dommages qu'il cause intentionnellement ou par négligence grave. Le site étant gratuit, sa responsabilité pour négligence légère est exclue, dans la mesure où la loi le permet. Il ne répond pas des contenus publiés par les utilisateurs, ni des sites vers lesquels le site renvoie.",
        ],
      },
      changes: {
        title: "Modifications et langue",
        intro: [
          "Ces conditions peuvent changer avec le site ; la date en tête dit quand elles ont été mises à jour pour la dernière fois. Une modification importante est annoncée par e-mail aux comptes au moins 14 jours avant de s'appliquer ; qui ne l'accepte pas peut faire supprimer son compte gratuitement d'ici là.",
          "La version française des présentes conditions fait foi ; la version anglaise en est une traduction.",
        ],
      },
      law: {
        title: "Droit applicable et contact",
        intro: [
          "Les présentes conditions sont soumises au droit suisse. Le for est à Genève, sous réserve des fors impératifs prévus par la loi, notamment en faveur des consommateurs.",
          "Le site est exploité par Daniel Garcia, personne privée, à Genève, en Suisse. Contact : {contact}.",
        ],
      },
    },
  },

  // Profile page: names and contact details, company, files and documents
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
  },

  // Credentials page: the e-mail address and the password of the account
  credentials: {
    title: "Mes identifiants",
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
    notifications: "Notifications",
    notify: "Recevoir un e-mail quand il y a du nouveau pour vous sur MarkeTech",
    notifySaved: "Enregistré.",
    notifyDemo: "Les comptes de démonstration ne reçoivent pas d'e-mails.",
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
    notFound: "Cette offre n'existe pas, ou n'est plus publiée.",
    // Applying, under the heading of an offer
    apply: "Postuler",
    loginToApply: "{login} pour postuler à cette offre.",
    loginLink: "Connectez-vous",
    applied: "Vous avez postulé le {date}",
    myApplicationsLink: "Mes candidatures",
    // The employer of the offer, under its heading
    yours: "Cette offre est la vôtre",
    editLink: "Modifier l'offre",
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
    companyLink: "Compléter mon profil",
    applications: "Aucune candidature | {count} candidature | {count} candidatures",
    favorites: "Aucun favori | {count} favori | {count} favoris",
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
    new: "Nouvelle",
    updated: "Mise à jour",
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

  // The heart on the offers, and the favorites of a candidate
  favorites: {
    add: "Ajouter à mes favoris",
    remove: "Retirer de mes favoris",
    loginToSave: "Connectez-vous pour mettre cette offre de côté",
  },
  myFavorites: {
    title: "Mes favoris",
    none: "Aucune offre mise de côté pour l'instant. Le cœur sur une offre la garde ici.",
    loadFailed: "Vos favoris n'ont pas pu être chargés.",
  },

  // The applications received by an employer, all of them or one offer's
  receivedApplications: {
    title: "Candidatures reçues",
    status: "État",
    allStatuses: "Tous",
    allApplications: "Toutes les candidatures",
    notFound: "Cette offre n'existe pas, ou n'est pas la vôtre.",
    loadFailed: "Les candidatures n'ont pas pu être chargées.",
    none: "Aucune candidature à afficher.",
    count: "Aucune candidature | {count} candidature | {count} candidatures",
    set: {
      in_progress: "Mettre en cours",
      accepted: "Accepter",
      rejected: "Refuser",
    },
    confirm: {
      in_progress: "Mettre en cours la candidature de {name} ? La conversation s'ouvre avec le candidat.",
      accepted: "Accepter la candidature de {name} ? La conversation sera close.",
      rejected: "Refuser la candidature de {name} ? La conversation sera close.",
    },
    firstMessage: "Premier message au candidat (facultatif)",
    lastMessage: "Dernier message au candidat (facultatif)",
  },

  // Messaging: the conversations of the applications in progress
  messaging: {
    openTitle: "Conversations ouvertes",
    closedTitle: "Conversations closes",
    noneOpen: "Aucune conversation ouverte. Une conversation s'ouvre quand l'employeur met une candidature en cours.",
    noneClosed: "Aucune conversation close. Une conversation se ferme quand la candidature est acceptée ou refusée.",
    loadFailed: "Les conversations n'ont pas pu être chargées.",
    notFound: "Cette conversation n'existe pas, ou n'est pas la vôtre.",
    you: "Vous :",
    button: "Messages",
    placeholder: "Votre message",
    hint: "Ctrl + Entrée pour envoyer",
    send: "Envoyer",
    read: "lu",
    emptyOpen: "Aucun message pour l'instant : écrivez le premier.",
    emptyClosed: "Aucun message n'a été échangé.",
    closed: {
      received: "La conversation s'ouvrira quand l'employeur prendra la candidature en charge.",
      accepted: "Conversation close : la candidature a été acceptée.",
      rejected: "Conversation close : la candidature a été refusée.",
    },
  },

  // Appointments: the cards in the conversation, the proposal, the calendar
  appointments: {
    title: "Rendez-vous",
    new: "Nouveau",
    pageTitle: "Mes rendez-vous",
    intro: {
      candidate: "Les rendez-vous proposés par les employeurs, à accepter ou refuser depuis la conversation ou ici.",
      employer: "Les rendez-vous proposés à vos candidats. Proposez-en un depuis la conversation d'une candidature en cours.",
    },
    loadFailed: "Les rendez-vous n'ont pas pu être chargés.",
    coming: "À venir",
    noneComing: "Aucun rendez-vous à venir.",
    clickHint: "Cliquez sur un rendez-vous du calendrier pour en voir le détail.",
    openConversation: "Ouvrir la conversation",
    proposed: "Proposé le {date}",
    propose: "Proposer un rendez-vous",
    accept: "Accepter",
    decline: "Refuser",
    cancel: "Annuler le rendez-vous",
    addToCalendar: "Ajouter à mon agenda",
    answerLabel: "Votre message (obligatoire)",
    cancelLabel: "Un mot pour le candidat (facultatif)",
    confirm: {
      accept: "Accepter le rendez-vous du {when} ?",
      decline: "Refuser le rendez-vous du {when} ?",
      cancel: "Annuler le rendez-vous du {when} ?",
    },
    answer: {
      candidate: "Votre réponse",
      employer: "Réponse du candidat",
    },
    cancellation: {
      candidate: "Message de l'employeur",
      employer: "Votre message",
    },
    state: {
      pending: "En attente",
      accepted: "Accepté",
      declined: "Refusé",
      cancelled: "Annulé",
      expired: "Expiré",
    },
    duration: {
      30: "30 minutes",
      45: "45 minutes",
      60: "1 heure",
      90: "1 heure 30",
    },
    form: {
      title: "Proposer un rendez-vous",
      when: "Date et heure",
      whenMissing: "Indiquez une date et une heure.",
      whenHint: "Du lundi au vendredi",
      weekend: "Un rendez-vous se propose un jour ouvrable, du lundi au vendredi.",
      duration: "Durée",
      place: "Lieu",
      placeHint: "Adresse, lien de visio ou « par téléphone »",
      note: "Précisions (facultatif)",
      send: "Proposer",
    },
  },

  // Reviews of the platform: the list, the bar on the right, one's own
  reviews: {
    title: "Avis sur la plateforme",
    intro: "Ce que les candidats et les employeurs pensent de MarkeTech.",
    asideTitle: "Avis des utilisateurs",
    summary: "Résumé des avis",
    count: "Aucun avis | {count} avis | {count} avis",
    stars: "{count} étoile | {count} étoile | {count} étoiles",
    outOfFive: "{value} sur 5",
    none: "Aucun avis pour l'instant.",
    loadFailed: "Les avis n'ont pas pu être chargés.",
    seeAll: "Voir tous les avis",
    giveYours: "Donner mon avis",
    changeYours: "Modifier mon avis",
    more: "Afficher plus d'avis",
    someone: "Un utilisateur",
    yours: "Votre avis",
    role: {
      candidate: "Candidat·e",
      employer: "Employeur",
    },
    changed: "modifié le {date}",
    criteria: {
      ease_of_use: "Facilité d'utilisation",
      offers_and_applications: "Offres et candidatures",
      messaging: "Messagerie",
      appointments: "Rendez-vous",
    },
    word: {
      1: "Mauvais",
      2: "Moyen",
      3: "Correct",
      4: "Bien",
      5: "Excellent",
    },
    choose: "Choisissez une note",
    mineTitle: "Mon avis",
    mineIntro: "Notez la plateforme de 1 à 5 étoiles, dans l'ensemble puis sur quatre points, et dites en quelques mots ce qui vous plaît ou ce qui vous manque.",
    overall: "Note générale",
    comment: "Votre commentaire",
    commentHint: "Ce qui vous a aidé, ce qui vous a manqué…",
    length: "{count} / {max}",
    signedCandidate: "Votre avis est public : il est signé de votre prénom et de l'initiale de votre nom.",
    signedEmployer: "Votre avis est public : il est signé de votre prénom, de l'initiale de votre nom et du nom de votre entreprise.",
    publish: "Publier mon avis",
    save: "Enregistrer",
    delete: "Supprimer mon avis",
    confirmDelete: "Supprimer votre avis ? Il disparaîtra de la liste publique.",
    published: "Avis publié",
    saved: "Avis enregistré",
    deleted: "Avis supprimé",
    demoLocked: "Compte de démo : l'avis de ce compte est affiché, mais il ne peut pas être modifié, car les avis sont publics.",
    noRole: "Un compte administrateur ne donne pas d'avis sur la plateforme.",
  },

  // About the project: what the site does, its technologies, its code
  about: {
    title: "À propos du projet",
    headerLink: "À propos du projet",
    footerLink: "À propos du projet",
    stack: "Python\u00a0· Django\u00a0· DRF\u00a0· Channels\u00a0· Vue\u00a03\u00a0· TypeScript\u00a0· Vite\u00a0· PostgreSQL\u00a0· Redis\u00a0· WebSocket\u00a0· nginx\u00a0· Docker\u00a0· GitHub\u00a0Actions",
    intro: [
      "MarkeTech est une plateforme d'offres d'emploi pour étudiants et jeunes diplômés en informatique : les employeurs publient des offres, les candidats postulent, et les deux échangent par messages et par rendez-vous jusqu'à la décision.",
      "Le site est né d'un projet d'équipe de la HEG Genève. Daniel Garcia l'a ensuite réécrit sans l'équipe d'origine, du code au déploiement, avec l'aide de Claude, l'assistant IA d'Anthropic : c'est cette version que décrit cette page.",
    ],
    features: {
      title: "Ce que fait le site",
      items: [
        "Offres d'emploi publiques, avec filtres (mot-clé, ville, pays, contrat, télétravail, salaire, date de publication) et pagination.",
        "Candidatures avec CV, lettre de motivation et documents, copiés au moment de l'envoi, et suivi de leur état des deux côtés.",
        "Messagerie entre le candidat et l'employeur pour chaque candidature en cours.",
        "Rendez-vous proposés par l'employeur, acceptés ou refusés par le candidat, dans un calendrier, et exportables vers un agenda (fichier .ics).",
        "Mises à jour en direct : les nouveaux messages et les nouvelles des candidatures apparaissent sans recharger la page, dans chaque onglet ouvert.",
        "E-mails de notification dans la langue de chacun, que chacun peut arrêter, et avis de sécurité après un changement d'adresse e-mail ou de mot de passe.",
        "Modération après publication : l'administrateur est averti de chaque offre et de chaque avis, et peut bloquer un compte.",
        "Favoris, avis sur la plateforme, interface et messages du serveur en français et en anglais.",
        "Deux comptes de démonstration ouverts à tous, remis à zéro chaque nuit.",
      ],
    },
    stackTitle: "Technologies",
    groups: {
      backend: {
        title: "Backend",
        items: [
          { name: "Python 3.13 et Django 6.1", text: "Les modèles, les migrations, l'interface d'administration, les traductions (gettext)." },
          { name: "Django REST Framework 3.18", text: "L'API JSON que lit le frontend, avec ses permissions par rôle et ses limites d'écriture." },
          { name: "django-allauth 65.19 (mode headless)", text: "Inscription, connexion par cookie de session, vérification de l'adresse e-mail, mot de passe oublié, avis de sécurité." },
          { name: "Channels 4.3 et channels-redis 4.3", text: "Les connexions WebSocket, et les signaux en direct envoyés aux onglets ouverts par Redis." },
          { name: "Daphne 4.2 et WhiteNoise 6.12", text: "Le serveur ASGI, pour HTTP et WebSocket, et les fichiers statiques de l'administration." },
          { name: "Pillow 13.0 et django-countries 9.1", text: "Le contrôle des images envoyées, la liste des pays dans la langue de l'interface." },
        ],
      },
      frontend: {
        title: "Frontend",
        items: [
          { name: "Vue 3.5 et TypeScript 6.0", text: "Une application à page unique, en composants à fichier unique et Composition API." },
          { name: "Vite 8.3 et vue-tsc 3.3", text: "Le serveur de développement et la compilation, qui échoue si les types d'un composant sont faux." },
          { name: "Vue Router 5.4 et vue-i18n 11.4", text: "La navigation, et l'interface en français et en anglais." },
          { name: "vue-cal 4.10", text: "Le calendrier des rendez-vous, chargé seulement quand la page s'ouvre." },
          { name: "Poppins (Fontsource)", text: "La police, servie par le site lui-même : aucune requête vers Google Fonts." },
        ],
      },
      data: {
        title: "Données",
        items: [
          { name: "PostgreSQL 18 et psycopg 3.3", text: "La base de données en production, dans son propre conteneur, et le pilote qui la relie à Django." },
          { name: "Redis 8", text: "La couche de canaux des mises à jour en direct, dans son propre conteneur, sans persistance : il ne transporte que des signaux." },
          { name: "SQLite", text: "La base de données en développement et pendant les tests de GitHub Actions, intégrée à Python." },
        ],
      },
      delivery: {
        title: "Livraison",
        items: [
          { name: "Docker et Docker Compose", text: "Quatre conteneurs : PostgreSQL, Redis, le backend, et le frontend compilé par Node.js 24 puis servi par nginx (version stable). La base de données et Redis sont sur un réseau interne, hors de portée d'Internet." },
          { name: "GitHub Actions", text: "À chaque push sur develop et main, les tests ; sur main, la construction des deux images et leur publication sur le registre de GitHub (ghcr.io). Les actions sont épinglées par commit." },
          { name: "Déploiement continu", text: "Le serveur, chez Infomaniak en Suisse, récupère la nouvelle version en moins de deux minutes ; les migrations s'appliquent au démarrage." },
        ],
      },
      operations: {
        title: "Exploitation",
        items: [
          { name: "Serveur Linux et reverse proxy", text: "Un VPS chez Infomaniak, avec nginx devant l'application pour le HTTPS ; l'adresse réelle du visiteur parvient à l'application, pour les limites contre les abus et les avis de sécurité." },
          { name: "restic et Swiss Backup", text: "Chaque nuit, la base de données, les fichiers et la configuration du serveur, chiffrés et envoyés vers Swiss Backup d'Infomaniak ; gardés 14 nuits, 8 semaines et 6 mois. La restauration suit une procédure écrite, testée en production." },
          { name: "Healthchecks.io", text: "Surveille la sauvegarde de la nuit et envoie une alerte par e-mail si elle échoue ou ne s'exécute pas." },
          { name: "Minuteries systemd", text: "Les mises à jour toutes les deux minutes, la remise à zéro de la démo et la sauvegarde chaque nuit." },
          { name: "E-mail par SMTP", text: "Le service de messagerie d'Infomaniak, avec un mot de passe d'appareil dédié ; un envoi raté est écrit au journal et ne bloque jamais l'action de l'utilisateur." },
        ],
      },
      quality: {
        title: "Qualité",
        items: [
          { name: "162 tests automatisés", text: "Modèles, API, droits d'accès, notifications, mises à jour en direct, modération et données de démonstration, lancés par GitHub Actions et vérifiés aussi sur PostgreSQL." },
          { name: "Règles en base de données", text: "Les règles importantes sont aussi des contraintes de la base : une candidature par offre et par candidat, un avis par compte, un rendez-vous en attente par candidature, des notes de 1 à 5, des fourchettes de salaire cohérentes, aucun message vide." },
        ],
      },
    },
    code: {
      title: "Le code",
      text: "Le code source du site est public sur GitHub, avec son historique.",
      link: "Voir le dépôt sur GitHub",
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
