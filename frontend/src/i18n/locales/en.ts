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
    notice: "Demo site",
  },

  // The two roles, as shown to the logged-in user (header menu, profile)
  roles: {
    candidate: "Candidate",
    employer: "Employer",
  },

  // Header: session state and links of the account
  header: {
    demo: "Try the demo",
    signup: "Sign up",
    login: "Log in",
    profile: "My profile",
    account: "Account menu",
    logout: "Log out",
  },

  // Side bar: the navigation of a logged-in user, one group per area
  nav: {
    label: "Main navigation",
    offers: "Offers",
    allOffers: "All the offers",
    myOffers: "My offers",
    myApplications: "My applications",
    myFavorites: "My favourites",
    receivedApplications: "Applications received",
    account: "My account",
    profile: "Profile",
    credentials: "Login details",
    messaging: "Messaging",
    openConversations: "Open",
    closedConversations: "Closed",
    appointments: "Appointments",
    platform: "Platform",
    allReviews: "All the reviews",
    myReview: "My review",
  },

  // Empty lists: the way to the place where they get filled
  empty: {
    browse: "See the offers",
  },

  // Public demonstration: the demo accounts of the login page
  demo: {
    title: "Try the demo",
    text: "Discover the site without an account, with a shared demo account reset every night.",
    terms: "By trying the demo, you accept the {terms} and have read the {privacy}.",
    candidate: "Candidate",
    employer: "Employer",
    unavailable: "The demo is not available at the moment.",
    band: "Demo account, reset every night.",
    locked: "Demo account: the e-mail address and the password cannot be changed.",
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
    terms: "Terms of use",
    privacy: "Privacy",
    copyright: "© {year} Daniel Garcia",
  },

  // Sign-up page
  signup: {
    title: "Create your account",
    firstName: "First name",
    lastName: "Last name",
    email: "E-mail address",
    password: "Password",
    passwordConfirm: "Confirm the password",
    role: "I am",
    candidate: "A candidate",
    employer: "An employer",
    terms: "I accept the {terms} and I have read the {privacy}.",
    termsLink: "terms of use",
    privacyLink: "privacy policy",
    termsRequired: "You must accept the terms of use to create an account.",
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
    forgotLink: "Forgot your password?",
  },

  // Address verification page, reached from the link in the e-mail
  verify: {
    title: "E-mail address verification",
    pending: "Checking your link…",
    confirmed: "Your e-mail address is confirmed. You can now log in.",
    changed: "Your new e-mail address is now in force.",
    invalid: "This link is invalid or has expired. Log in: if your address is still unconfirmed, you will receive a new link.",
    invalidLoggedIn: "This link is invalid or has expired. Your current address stays in force; you can ask again from your login details.",
    loginLink: "Log in",
    credentialsLink: "Back to my login details",
  },

  // Password reset: the page that asks for the link
  passwordReset: {
    title: "Reset your password",
    intro: "Enter your e-mail address: we will send you a link to choose a new password.",
    email: "E-mail address",
    submit: "Send the link",
    sent: "We have sent an e-mail to {email}. Open it and follow its link to choose a new password.",
  },

  // Password reset: the page reached from the link in the e-mail
  newPassword: {
    title: "Choose a new password",
    password: "New password",
    passwordConfirm: "Confirm the new password",
    submit: "Save the new password",
    done: "Your password is changed. You can now log in.",
    invalid: "This link is invalid or has expired.",
    requestLink: "Request a new link",
    loginLink: "Log in",
  },

  // Privacy page: what the site does with the data of its users, section by
  // section. Each section has a title and opening paragraphs; some add a list
  // of terms with their text, and closing paragraphs.
  privacy: {
    title: "Privacy policy",
    updated: "Last updated: 29 October 2026",
    sections: {
      summary: {
        title: "In short",
        intro: [
          "MarkeTech is a demonstration project without commercial activity, run by Daniel Garcia in Geneva.",
          "The site only stores what its features need and uses it for nothing else: no advertising, no tracking, no audience measurement, no profiling.",
          "Everything is hosted in Switzerland, at Infomaniak. No data is sold or passed on.",
          "Only the published offers and the reviews are public. Your documents are seen only by the employers you apply to.",
          "You can see, correct and have deleted your data at any time, by writing to {contact}.",
        ],
      },
      controller: {
        title: "Who is responsible",
        intro: [
          "MarkeTech is a job board for students and young graduates in computer science, built by Daniel Garcia to show his work. It works like a real platform, but nobody gets hired through it.",
          "The person responsible for the processing of your data is Daniel Garcia, a private person, in Geneva, Switzerland. For any question about this page or about your data, write to {contact}.",
          "The site is there to be tried out. You do not need real documents to do so, and nothing you enter is used for anything else than running the site.",
        ],
      },
      data: {
        title: "Data processed and why",
        intro: ["The site only stores what its features need. Depending on what you do, that is:"],
        items: [
          { term: "Account", text: "E-mail address, password (stored hashed, never readable), first name, last name, role (candidate or employer), whether the address is verified, dates of sign-up and of last login, date you accepted the terms of use, language of the interface (noted at login and when you change it) and whether you receive the notification e-mails. Purpose: to identify you and to write to you." },
          { term: "Candidate profile", text: "Postal address, phone number, photo, CV and any other document you attach. Purpose: to apply to offers without entering them again." },
          { term: "Employer profile", text: "Postal address, phone number, photo, and the company: name, address, phone number, logo. Only the name and the logo of the company are public, with the offers; your own details and your photo stay private." },
          { term: "Job offers", text: "Title, description, city and country, type of contract, workload, remote work, salary range with its currency and period, years of experience asked, date of publication; the name and the logo of the company are read on the profile of the employer. A published offer is visible to every visitor of the site; a draft or a closed offer, to its employer only. A published offer must be closed before it can be deleted, and an offer that received applications can only be closed, so that the candidates keep the trace of their application." },
          { term: "Applications", text: "The offer applied to, the CV and cover letter submitted, the documents of your profile you join to it (copied when it is sent: changing your profile afterwards does not change what the employer received), the date, the status (received, in progress, accepted, rejected), the history of its changes and when each was seen. An application is seen by the candidate and by the employer who published the offer; the employer also sees your first name, last name, e-mail address, phone number and city, never your postal address nor your photo. You may withdraw it as long as the employer has not decided: it is then deleted with its files." },
          { term: "Messages", text: "Exchanged between a candidate and the employer of the offer about an application: the text, the date it was sent and the date the other one read it. The conversation opens when the employer moves the application in progress; once the application is accepted or rejected, it stays readable, but nobody can write in it any more. The two participants can read it, nobody else. It is deleted with the application." },
          { term: "Appointments", text: "Proposed by an employer about an application in progress: date, time and length, place, any details; then the candidate's answer and their message, or the employer's cancellation and any message with it. Seen by the two participants only; each can export it to a calendar (.ics file), with the offer, the other participant, the place and the details." },
          { term: "Favourites", text: "The offers a candidate has set aside, with the date. They are seen by the candidate only; the employer of an offer is told how many candidates set it aside, never which ones." },
          { term: "Reviews of the platform", text: "An overall rating, four detailed ratings and a comment, published with your first name, the initial of your last name and your role (for an employer, the name of the company), visible to every visitor. One review per account, which you may change or delete at any time; the demo accounts cannot publish one." },
          { term: "Security notices", text: "When the e-mail address or the password of your account changes, the site writes to you (to the former address for a change of address) with the IP address, the browser and the time of the request, so that you can spot a change you did not make. The IP address is only written in this e-mail; the site stores it nowhere." },
          { term: "Moderation", text: "Every review written or changed, and every offer published or changed while published, is sent by e-mail to the administrator, with its text and the name and e-mail address of its author, so that unlawful content can be withdrawn quickly." },
          { term: "Protection against abuse", text: "To slow down attacks on the login and the sign-up, the site counts the attempts by IP address and by e-mail address, in memory only, for a few minutes. It also limits the number of changes each account can make per hour." },
          { term: "Technical data", text: "The servers keep technical logs (requests received, with the IP address, the date, the page and the browser) for security and troubleshooting only." },
          { term: "Live updates", text: "While you are logged in, each open tab keeps a connection (WebSocket) with the server, authenticated by your session cookie, so that new messages and news appear without reloading the page. It only carries signals without content, and stores nothing." },
        ],
        outro: [
          "The administrator of the site sees this data in its administration interface, to run the site and to answer your requests.",
          "The two demo accounts are shared by every visitor: what you write or upload with them is seen by the next ones, until they are reset every night. Put nothing personal in them.",
        ],
      },
      bases: {
        title: "On what basis",
        intro: [
          "Under Swiss law, the site processes your data in line with the principles of the Federal Act on Data Protection (FADP). For visitors in the European Union, to whom the General Data Protection Regulation (GDPR) may apply, the bases are:",
        ],
        items: [
          { term: "Running the service (GDPR, art. 6(1)(b))", text: "Your account, your profile, the offers, the applications, the messages, the appointments, the favourites, the reviews, and the e-mails about them: what you ask the site to do." },
          { term: "Legitimate interest (GDPR, art. 6(1)(f))", text: "The security of the site and of your account (logs, limits against abuse, security notices), the moderation of public content and the backups. The interest is to keep the site safe and lawful; you may object to it (see \"Your rights\")." },
        ],
      },
      recipients: {
        title: "Who receives your data",
        intro: ["Your data is shown or passed only to:"],
        items: [
          { term: "The other users", text: "As far as the features imply: an employer sees the applications to its offers, a candidate sees the company behind an offer, the participants of a conversation or an appointment see what concerns it." },
          { term: "The public", text: "The published offers (with the name and the logo of the company) and the reviews (first name, initial of the last name, role, company)." },
          { term: "Infomaniak", text: "Infomaniak Network SA, in Geneva, hosts the server, keeps its encrypted backups and sends its e-mails, on behalf of the site and in Switzerland." },
          { term: "Other services", text: "GitHub hosts the public source code and the images of the application, and Healthchecks.io watches that the nightly backup ran: neither receives data of the users." },
        ],
        outro: ["No data is sold, rented or passed on to anyone else."],
      },
      abroad: {
        title: "Data abroad",
        intro: [
          "Your data stays in Switzerland and is not communicated to another country. The e-mails sent to your own address go, of course, to the mail provider you chose.",
        ],
      },
      retention: {
        title: "How long data is kept",
        intro: ["Your data is kept only as long as it is needed:"],
        items: [
          { term: "Account and content", text: "As long as your account exists. What you delete yourself (a document, a photo, a favourite, a review, a withdrawn application, an offer that may be deleted) disappears from the site at once, files included. When an account is deleted, everything attached to it goes with it; for an employer, so do the applications to its offers." },
          { term: "Backups", text: "Data deleted from the site remains for a while in the encrypted backups, which are erased automatically after six months at most." },
          { term: "Technical logs", text: "Erased automatically: the server keeps only a limited volume of them, the oldest lines being replaced by the newest." },
          { term: "Moderation e-mails", text: "Deleted once handled." },
          { term: "Demo accounts", text: "Reset every night, with everything done with them." },
        ],
        outro: ["To have your account deleted, write to {contact} from the address of the account."],
      },
      cookies: {
        title: "Cookies and local storage",
        intro: [
          "The site sets no third-party cookie, uses no tracker and shows no advertising. It keeps in your browser only what it needs to work, which is why it asks for no consent:",
        ],
        items: [
          { term: "sessionid", text: "A cookie that keeps you logged in; it lasts two weeks at most and is deleted when you log out. Sent over HTTPS only, and out of reach of the scripts of the page." },
          { term: "csrftoken", text: "A cookie that protects the forms against requests forged by another site; it lasts one year. Sent over HTTPS only." },
          { term: "marketech.locale", text: "The language you chose, kept in the local storage of your browser until you clear it." },
        ],
        outro: [
          "You can delete or block them in your browser: the site then forgets your language, and you can no longer log in. The font of the site is served by the site itself, without any request to Google or another provider.",
        ],
      },
      security: {
        title: "Security",
        intro: [
          "The whole site is served over HTTPS. Passwords are stored hashed, never in clear. The photos and the documents you upload are private: the site checks who asks for them before handing them over, and no address leads to them directly. The documents of an application are seen by the candidate and by the employer of the offer; only the logo of the company is public, since it goes with the offers. The database cannot be reached from the Internet, the backups are encrypted, and access to the server is reserved to its administrator.",
          "Should a breach of security put your data at high risk, the site informs the Federal Data Protection and Information Commissioner (FDPIC) and, where it is needed for your protection, tells you directly by e-mail.",
        ],
      },
      rights: {
        title: "Your rights",
        intro: [
          "You can ask what data the site holds about you and receive a copy of it, also in a common electronic format to take it elsewhere; have it corrected; have it deleted; and object to a processing based on a legitimate interest. Write to {contact}, from the address of your account if you have one: the answer is free of charge and comes within 30 days. You can also change most of your data yourself, from your account.",
          "If you think your rights are not respected, you can turn to the Federal Data Protection and Information Commissioner (FDPIC, www.edoeb.admin.ch). If you live in the European Union, you can also turn to the data protection authority of your country, for instance the CNIL in France.",
        ],
      },
      automated: {
        title: "No automated decision",
        intro: [
          "No decision is taken by a machine: the site does not sort, score or filter the candidates; the employers read the applications themselves.",
          "Put no sensitive data in your documents (health, religion, political opinions, copy of an identity card, AVS number): the site does not need it.",
        ],
      },
      changes: {
        title: "Changes to this page",
        intro: [
          "This page describes the site as it is. It changes when the site changes, and the date at the top says when it was last updated. An important change is announced by e-mail to the accounts.",
        ],
      },
    },
  },

  // Terms of use, accepted at sign-up: sections in the same shape as the
  // privacy page (title and paragraphs)
  terms: {
    title: "Terms of use",
    updated: "Last updated: 29 October 2026",
    sections: {
      essentials: {
        title: "Important points",
        intro: [
          "MarkeTech is a demonstration project: free, without commercial activity, and nobody is hired through it. The offers published on it are examples.",
          "The two demo accounts are public and reset every night: never put real or personal data in them.",
          "What you publish goes online at once; the administrator reads it afterwards and may withdraw it or block the account.",
          "The site is provided without warranty and may stop; its author is liable only for damage caused intentionally or by gross negligence.",
          "These terms may change; an important change is announced by e-mail 14 days in advance.",
        ],
      },
      purpose: {
        title: "What MarkeTech is",
        intro: [
          "MarkeTech is a demonstration project built by Daniel Garcia, in Geneva, to show his work: a job board for students and young graduates in computer science. It has no commercial activity: no offer commits anyone, nobody is hired through it, and nothing is sold on it.",
          "MarkeTech is not an employment agency: it does not select candidates, takes no part in the conclusion of an employment contract and receives no remuneration from anyone.",
          "The offers on the site are examples made to try it out. Do not publish a real vacancy expecting real applications.",
        ],
      },
      acceptance: {
        title: "Acceptance",
        intro: [
          "You accept these terms by ticking the box of the sign-up form when you create an account, or the box of the login page when you open a demo account. If you do not accept them, do not use the site.",
        ],
      },
      account: {
        title: "Your account",
        intro: [
          "The site is open to people aged 18 or over. An account is personal: one person, an e-mail address that is yours, a password you keep to yourself. You choose your role when you sign up, candidate or employer, and you are responsible for what is done with your account.",
          "Two demo accounts, a candidate and an employer, open without password from the login page. Every visitor shares them, their address and password cannot be changed, and they are reset every night: everything done with them goes, including what links your own account to them (an application to one of their offers, its messages, your favourites among those offers). Your account itself and what depends on it alone stay.",
        ],
      },
      use: {
        title: "Using the site",
        intro: [
          "The site is there to be tried out. You do not need to put real documents or real data on it, and you do not put another person's data on it without their consent.",
          "It is forbidden to pass yourself off as someone else, to try to reach an account or data that are not yours, to copy the content of the site with automated means, or to disturb its working. To protect the site, each account may make up to 300 changes per hour (60 for a demo account), and the login and sign-up attempts are limited.",
        ],
      },
      offers: {
        title: "Offers",
        intro: [
          "An employer answers for the offers it publishes. An offer describes one position, fairly; it does not discriminate on grounds of sex, origin, nationality, age, religion, disability or sexual orientation, and it asks no payment from the candidates. Use only a logo and images you have the right to use.",
          "A published offer must be closed before it can be deleted; an offer that received applications can only be closed.",
        ],
      },
      exchanges: {
        title: "Applications, messages, appointments and reviews",
        intro: [
          "A candidate may withdraw an application as long as the employer has not decided. Put no copy of an identity document, no AVS number and no health data in your documents.",
          "The messages and the appointments are about the application only, and stay courteous.",
          "A review is about the platform: honest, without insults, naming no other person. One review per account; the demo accounts cannot publish one.",
        ],
      },
      prohibited: {
        title: "Prohibited content and reporting",
        intro: [
          "It is forbidden to publish unlawful content, in particular content that attacks the honour or the personality of someone, incites to discrimination or hatred, or infringes copyright; misleading content, spam or advertising; and the personal data of another person without their consent.",
          "To report content, write to {contact}, saying where it is: the report is examined promptly.",
        ],
      },
      moderation: {
        title: "Moderation",
        intro: [
          "What you publish goes online at once; the administrator is alerted and reads it afterwards. He may withdraw content contrary to these terms or to the law, and block an account: its offers and its review are then hidden, nothing is deleted, and the block can be lifted. Unless it is urgent, he tells the person concerned and gives the reason.",
        ],
      },
      licence: {
        title: "What you publish",
        intro: [
          "What you publish (profile, offers, documents, messages, review) remains yours. You allow the site, free of charge and for as long as it stays online, to store it and to show it to the people its features imply, and to every visitor for a published offer or a review, for the working of the site only. You guarantee that you hold the rights to it.",
        ],
      },
      end: {
        title: "End of use",
        intro: [
          "You can stop using the site at any time and have your account deleted by writing to {contact} from the address of the account; everything attached to it is deleted with it, as the privacy policy describes.",
          "An account that breaks these terms may be blocked or deleted. If the site is to stop for good, the accounts are told by e-mail 30 days in advance, so that everyone can retrieve their documents.",
        ],
      },
      availability: {
        title: "No warranty",
        intro: [
          "The site is provided free of charge, as it is, with no warranty of availability, of continuity, or of accuracy of the offers, nor that an application gets an answer: it may change or be interrupted at any time. Keep your own copy of your documents.",
        ],
      },
      liability: {
        title: "Liability",
        intro: [
          "Daniel Garcia is liable for damage he causes intentionally or by gross negligence. Since the site is free, his liability for slight negligence is excluded, as far as the law allows. He is not liable for the content published by the users, nor for the sites the site links to.",
        ],
      },
      changes: {
        title: "Changes and language",
        intro: [
          "These terms may change with the site; the date at the top says when they were last updated. An important change is announced by e-mail to the accounts at least 14 days before it applies; whoever does not accept it can have their account deleted free of charge before then.",
          "The French version of these terms prevails; the English version is a translation.",
        ],
      },
      law: {
        title: "Applicable law and contact",
        intro: [
          "These terms are governed by Swiss law. The courts of Geneva have jurisdiction, subject to the mandatory jurisdictions provided by law, in particular in favour of consumers.",
          "The site is run by Daniel Garcia, a private person, in Geneva, Switzerland. Contact: {contact}.",
        ],
      },
    },
  },

  // Profile page: names and contact details, company, files and documents
  profile: {
    title: "My profile",
    identity: "Identity",
    firstName: "First name",
    lastName: "Last name",
    contact: "Contact details",
    phone: "Phone",
    address: "Address",
    postalCode: "Postal code",
    city: "City",
    country: "Country",
    noCountry: "Not specified",
    company: "Company",
    companyName: "Company name",
    companyAddress: "Address",
    companyPostalCode: "Postal code",
    companyCity: "City",
    companyCountry: "Country",
    companyPhone: "Phone",
    save: "Save",
    saved: "Saved.",
    photo: "Photo",
    logo: "Logo",
    files: "Documents",
    cv: "CV",
    documents: "Other documents",
    noFile: "No file yet.",
    choose: "Choose a file",
    replace: "Replace",
    remove: "Remove",
    add: "Add a document",
    sending: "Sending…",
    fileSaved: "File saved.",
    fileRemoved: "File removed.",
    rules: "{types} · up to {size} MB",
    limit: "You have reached the limit of {max} documents.",
    confirmRemove: "Remove this file?",
    addedOn: "added on {date}",
    loadFailed: "Your profile cannot be loaded. Please try again later.",
    tooBig: "This file is bigger than {size} MB.",
    wrongType: "This type of file is not accepted ({types}).",
  },

  // Credentials page: the e-mail address and the password of the account
  credentials: {
    title: "My login details",
    email: "E-mail address",
    currentEmail: "Current address: {email}",
    newEmail: "New e-mail address",
    changeEmail: "Change the address",
    emailSent: "E-mail sent. Open it and follow its link: your current address stays in force until then.",
    emailPending: "Confirmation pending for {email}.",
    cancel: "Cancel",
    password: "Password",
    currentPassword: "Current password",
    newPassword: "New password",
    newPasswordConfirm: "Confirm the new password",
    changePassword: "Change the password",
    passwordChanged: "Password changed.",
    notifications: "Notifications",
    notify: "Receive an e-mail when there is something new for you on MarkeTech",
    notifySaved: "Saved.",
    notifyDemo: "The demo accounts receive no e-mail.",
  },

  // Job offers: the public list, its filters, and the detail of an offer
  offers: {
    title: "Job offers",
    count: "No offer | {count} offer | {count} offers",
    filters: "Filters",
    search: "Search",
    reset: "Reset",
    keyword: "Keyword",
    keywordHint: "In the title",
    city: "City",
    country: "Country",
    anyCountry: "Any country",
    contractLabel: "Contract",
    anyContract: "Any contract",
    remoteLabel: "Remote work",
    anyRemote: "Any",
    salaryMin: "Minimum salary",
    publishedAfter: "Published since",
    none: "No offer matches these criteria.",
    loadFailed: "The offers could not be loaded.",
    page: "Page {page} of {pages}",
    previous: "Previous",
    next: "Next",
    publishedOn: "Published on {date}",
    detailsLink: "View the offer",
    notFound: "This offer does not exist, or is no longer published.",
    // Applying, under the heading of an offer
    apply: "Apply",
    loginToApply: "{login} to apply to this offer.",
    loginLink: "Log in",
    applied: "You applied on {date}",
    myApplicationsLink: "My applications",
    // The employer of the offer, under its heading
    yours: "This offer is yours",
    editLink: "Edit the offer",
    description: "The position",
    facts: "In short",
    place: "Place",
    salaryLabel: "Salary",
    currencyLabel: "Currency",
    periodLabel: "Period",
    experienceLabel: "Experience",
    contract: {
      permanent: "Permanent",
      fixed_term: "Fixed term",
      internship: "Internship",
      student: "Student job",
    },
    remote: {
      on_site: "On site",
      hybrid: "Hybrid",
      remote: "Remote",
    },
    period: {
      month: "per month",
      year: "per year",
    },
    salary: {
      range: "{currency} {range} {period}",
      from: "From {currency} {amount} {period}",
      upTo: "Up to {currency} {amount} {period}",
    },
    status: {
      draft: "Draft",
      published: "Published",
      closed: "Closed",
    },
    experience: "{count} year of experience | {count} years of experience",
  },

  // The offers of an employer: the list with its moves
  myOffers: {
    title: "My offers",
    new: "New offer",
    none: "You have no offer yet. Create the first one: it stays a draft until you publish it.",
    loadFailed: "Your offers could not be loaded.",
    edit: "Edit",
    publish: "Publish",
    republish: "Publish again",
    close: "Close",
    delete: "Delete",
    confirmDelete: "Delete the offer \"{title}\"? It cannot be recovered.",
    companyLink: "Complete my profile",
    applications: "No application | {count} application | {count} applications",
    favorites: "No favourite | {count} favourite | {count} favourites",
  },

  // The form of an offer, new or changed
  offerForm: {
    newTitle: "New offer",
    editTitle: "Edit the offer",
    back: "My offers",
    notFound: "This offer does not exist, or is not yours.",
    title: "Title",
    description: "Description",
    descriptionHint: "The job, the team, the profile sought. Line breaks are kept.",
    city: "City",
    country: "Country",
    chooseCountry: "Choose a country",
    contract: "Contract",
    chooseContract: "Choose a contract",
    remote: "Remote work",
    workload: "Workload (%)",
    workloadMax: "Maximum workload",
    workloadHint: "From the first figure to the second; the same figure in both for a fixed workload.",
    experience: "Years of experience asked",
    salary: "Gross salary",
    salaryMax: "Maximum salary",
    salaryHint: "Minimum and maximum, or only one of them; leave both empty to say nothing.",
    required: "This field is required.",
    save: "Save",
    saveAndPublish: "Save and publish",
    saveAndRepublish: "Save and publish again",
  },

  // Job applications: what the candidate's and the employer's pages share
  applications: {
    new: "New",
    updated: "Updated",
    status: {
      received: "Received",
      in_progress: "In progress",
      accepted: "Accepted",
      rejected: "Rejected",
    },
    // One step of the history: "In progress on 14 October"
    historyStep: "{status} on {date}",
    sentOn: "Sent on {date}",
    cv: "CV",
    coverLetter: "Cover letter",
  },

  // Applying to an offer: the form of a candidate
  apply: {
    title: "Apply",
    back: "Back to the offer",
    notOpen: "This offer is not open to applications.",
    alreadyApplied: "You have already applied to this offer.",
    myApplicationsLink: "See my applications",
    cv: "CV",
    cvProfile: "The CV of my profile ({name})",
    cvOther: "Another file",
    cvNone: "Your profile has no CV yet: send one here, or keep one in your profile to join it in one click.",
    cvRequired: "Choose a CV.",
    coverLetter: "Cover letter (optional)",
    choose: "Choose a file",
    replace: "Replace",
    remove: "Remove",
    documents: "Documents of my profile to join",
    documentsNone: "Your profile has no document.",
    profileLink: "Add some",
    fileHint: "{types}, {size} MB at most.",
    tooBig: "This file is bigger than {size} MB.",
    wrongType: "This type of file is not accepted ({types}).",
    submit: "Send my application",
  },

  // The applications of a candidate: the list with the withdrawal
  myApplications: {
    title: "My applications",
    none: "You have not applied yet. The offers are on the home page.",
    loadFailed: "Your applications could not be loaded.",
    offerLink: "View the offer",
    offerClosed: "offer closed",
    withdraw: "Withdraw",
    confirmWithdraw: "Withdraw your application to \"{title}\"? Its files will be deleted.",
  },

  // The heart on the offers, and the favorites of a candidate
  favorites: {
    add: "Add to my favourites",
    remove: "Remove from my favourites",
    loginToSave: "Log in to put this offer aside",
  },
  myFavorites: {
    title: "My favourites",
    none: "No offer put aside yet. The heart on an offer keeps it here.",
    loadFailed: "Your favourites could not be loaded.",
  },

  // The applications received by an employer, all of them or one offer's
  receivedApplications: {
    title: "Applications received",
    status: "Status",
    allStatuses: "All",
    allApplications: "All applications",
    notFound: "This offer does not exist, or is not yours.",
    loadFailed: "The applications could not be loaded.",
    none: "No application to show.",
    count: "No application | {count} application | {count} applications",
    set: {
      in_progress: "Mark in progress",
      accepted: "Accept",
      rejected: "Reject",
    },
    confirm: {
      in_progress: "Move the application of {name} in progress? The conversation with the candidate opens.",
      accepted: "Accept the application of {name}? The conversation will be closed.",
      rejected: "Reject the application of {name}? The conversation will be closed.",
    },
    firstMessage: "First message to the candidate (optional)",
    lastMessage: "Last message to the candidate (optional)",
  },

  // Messaging: the conversations of the applications in progress
  messaging: {
    openTitle: "Open conversations",
    closedTitle: "Closed conversations",
    noneOpen: "No open conversation. A conversation opens when the employer moves an application in progress.",
    noneClosed: "No closed conversation. A conversation closes when the application is accepted or rejected.",
    loadFailed: "The conversations could not be loaded.",
    notFound: "This conversation does not exist, or is not yours.",
    you: "You:",
    button: "Messages",
    placeholder: "Your message",
    hint: "Ctrl + Enter to send",
    send: "Send",
    read: "read",
    emptyOpen: "No message yet: write the first one.",
    emptyClosed: "No message was exchanged.",
    closed: {
      received: "The conversation will open when the employer takes up the application.",
      accepted: "Conversation closed: the application was accepted.",
      rejected: "Conversation closed: the application was rejected.",
    },
  },

  // Appointments: the cards in the conversation, the proposal, the calendar
  appointments: {
    title: "Appointment",
    new: "New",
    pageTitle: "My appointments",
    intro: {
      candidate: "The appointments employers propose to you, to accept or decline from the conversation or here.",
      employer: "The appointments proposed to your candidates. Propose one from the conversation of an application in progress.",
    },
    loadFailed: "The appointments could not be loaded.",
    coming: "Coming up",
    noneComing: "No appointment coming up.",
    clickHint: "Click an appointment in the calendar to see its details.",
    openConversation: "Open the conversation",
    proposed: "Proposed on {date}",
    propose: "Propose an appointment",
    accept: "Accept",
    decline: "Decline",
    cancel: "Cancel the appointment",
    addToCalendar: "Add to my calendar",
    answerLabel: "Your message (required)",
    cancelLabel: "A word for the candidate (optional)",
    confirm: {
      accept: "Accept the appointment of {when}?",
      decline: "Decline the appointment of {when}?",
      cancel: "Cancel the appointment of {when}?",
    },
    answer: {
      candidate: "Your answer",
      employer: "The candidate's answer",
    },
    cancellation: {
      candidate: "The employer's message",
      employer: "Your message",
    },
    state: {
      pending: "Pending",
      accepted: "Accepted",
      declined: "Declined",
      cancelled: "Cancelled",
      expired: "Expired",
    },
    duration: {
      30: "30 minutes",
      45: "45 minutes",
      60: "1 hour",
      90: "1 hour 30",
    },
    form: {
      title: "Propose an appointment",
      when: "Date and time",
      whenMissing: "Give a date and a time.",
      whenHint: "Monday to Friday",
      weekend: "An appointment is proposed on a working day, from Monday to Friday.",
      duration: "Length",
      place: "Place",
      placeHint: "Address, video link or \"by phone\"",
      note: "Details (optional)",
      send: "Propose",
    },
  },

  // Reviews of the platform: the list, the bar on the right, one's own
  reviews: {
    title: "Reviews of the platform",
    intro: "What candidates and employers think of MarkeTech.",
    asideTitle: "User reviews",
    summary: "Summary of the reviews",
    count: "No review | {count} review | {count} reviews",
    stars: "{count} star | {count} star | {count} stars",
    outOfFive: "{value} out of 5",
    none: "No review yet.",
    loadFailed: "The reviews could not be loaded.",
    seeAll: "See all the reviews",
    giveYours: "Give my review",
    changeYours: "Change my review",
    more: "Show more reviews",
    someone: "A user",
    yours: "Your review",
    role: {
      candidate: "Candidate",
      employer: "Employer",
    },
    changed: "changed on {date}",
    criteria: {
      ease_of_use: "Ease of use",
      offers_and_applications: "Offers and applications",
      messaging: "Messaging",
      appointments: "Appointments",
    },
    word: {
      1: "Poor",
      2: "Fair",
      3: "Okay",
      4: "Good",
      5: "Excellent",
    },
    choose: "Choose a score",
    mineTitle: "My review",
    mineIntro: "Rate the platform from 1 to 5 stars, overall then on four points, and say in a few words what you like or what you miss.",
    overall: "Overall rating",
    comment: "Your comment",
    commentHint: "What helped you, what you missed…",
    length: "{count} / {max}",
    signedCandidate: "Your review is public: it is signed with your first name and the initial of your last name.",
    signedEmployer: "Your review is public: it is signed with your first name, the initial of your last name and the name of your company.",
    publish: "Publish my review",
    save: "Save",
    delete: "Delete my review",
    confirmDelete: "Delete your review? It will leave the public list.",
    published: "Review published",
    saved: "Review saved",
    deleted: "Review deleted",
    demoLocked: "Demo account: the review of this account is shown, but it cannot be changed, as the reviews are public.",
    noRole: "An administrator account does not review the platform.",
  },

  // About the project: what the site does, its technologies, its code
  about: {
    title: "About the project",
    headerLink: "About the project",
    footerLink: "About the project",
    stack: "Python\u00a0· Django\u00a0· DRF\u00a0· Channels\u00a0· Vue\u00a03\u00a0· TypeScript\u00a0· Vite\u00a0· PostgreSQL\u00a0· Redis\u00a0· WebSocket\u00a0· nginx\u00a0· Docker\u00a0· GitHub\u00a0Actions",
    intro: [
      "MarkeTech is a job board for students and young graduates in computer science: employers publish offers, candidates apply, and both talk through messages and appointments until the decision.",
      "The site started as a team project at the HEG Genève. Daniel Garcia then rewrote it without the original team, from the code to the deployment, with the help of Claude, the AI assistant made by Anthropic: this page describes that version.",
    ],
    features: {
      title: "What the site does",
      items: [
        "Public job offers, with filters (keyword, city, country, contract, remote work, salary, publication date) and pages.",
        "Applications with a CV, a cover letter and documents, copied when sent, and their status followed on both sides.",
        "Messaging between the candidate and the employer for every application in progress.",
        "Appointments proposed by the employer, accepted or declined by the candidate, in a calendar, and exported to an agenda (.ics file).",
        "Live updates: new messages and news of the applications appear without reloading the page, in every open tab.",
        "Notification e-mails in the language of each user, which anyone can stop, and security notices after a change of e-mail address or password.",
        "Moderation after publication: the administrator is alerted of every offer and every review, and can block an account.",
        "Favourites, reviews of the platform, interface and server messages in French and in English.",
        "Two demo accounts open to everyone, reset every night.",
      ],
    },
    stackTitle: "Technologies",
    groups: {
      backend: {
        title: "Backend",
        items: [
          { name: "Python 3.13 and Django 6.1", text: "The models, the migrations, the admin interface, the translations (gettext)." },
          { name: "Django REST Framework 3.18", text: "The JSON API read by the frontend, with its permissions by role and its limits on writes." },
          { name: "django-allauth 65.19 (headless mode)", text: "Sign-up, login with a session cookie, e-mail verification, forgotten password, security notices." },
          { name: "Channels 4.3 and channels-redis 4.3", text: "The WebSocket connections, and the live signals sent to the open tabs through Redis." },
          { name: "Daphne 4.2 and WhiteNoise 6.12", text: "The ASGI server, for HTTP and WebSocket, and the static files of the admin interface." },
          { name: "Pillow 13.0 and django-countries 9.1", text: "The check of uploaded images, the list of countries in the language of the interface." },
        ],
      },
      frontend: {
        title: "Frontend",
        items: [
          { name: "Vue 3.5 and TypeScript 6.0", text: "A single-page application, in single-file components and the Composition API." },
          { name: "Vite 8.3 and vue-tsc 3.3", text: "The development server and the build, which fails if the types of a component are wrong." },
          { name: "Vue Router 5.4 and vue-i18n 11.4", text: "The navigation, and the interface in French and in English." },
          { name: "vue-cal 4.10", text: "The calendar of the appointments, loaded only when its page opens." },
          { name: "Poppins (Fontsource)", text: "The font, served by the site itself: no request to Google Fonts." },
        ],
      },
      data: {
        title: "Data",
        items: [
          { name: "PostgreSQL 18 and psycopg 3.3", text: "The database in production, in its own container, and the driver that links it to Django." },
          { name: "Redis 8", text: "The channel layer of the live updates, in its own container, without persistence: it only carries signals." },
          { name: "SQLite", text: "The database in development and during the tests on GitHub Actions, built into Python." },
        ],
      },
      delivery: {
        title: "Delivery",
        items: [
          { name: "Docker and Docker Compose", text: "Four containers: PostgreSQL, Redis, the backend, and the frontend built with Node.js 24 then served by nginx (stable version). The database and Redis sit on an internal network, out of reach of the Internet." },
          { name: "GitHub Actions", text: "On every push to develop and main, the tests; on main, the build of the two images and their publication on GitHub's registry (ghcr.io). The actions are pinned by commit." },
          { name: "Continuous deployment", text: "The server, at Infomaniak in Switzerland, pulls the new version within two minutes; the migrations run at start-up." },
        ],
      },
      operations: {
        title: "Operations",
        items: [
          { name: "Linux server and reverse proxy", text: "A VPS at Infomaniak, with nginx in front of the application for HTTPS; the real address of the visitor reaches the application, for the limits against abuse and the security notices." },
          { name: "restic and Swiss Backup", text: "Every night, the database, the files and the configuration of the server, encrypted and sent to Infomaniak's Swiss Backup; kept 14 nights, 8 weeks and 6 months. The restore follows a written procedure, tested in production." },
          { name: "Healthchecks.io", text: "Watches the nightly backup and sends an alert by e-mail when it fails or does not run." },
          { name: "systemd timers", text: "The updates every two minutes, the reset of the demo and the backup every night." },
          { name: "E-mail by SMTP", text: "Infomaniak's mail service, with its own device password; a failed sending is written to the log and never breaks the action of the user." },
        ],
      },
      quality: {
        title: "Quality",
        items: [
          { name: "162 automated tests", text: "Models, API, access rights, notifications, live updates, moderation and demo data, run by GitHub Actions and also checked on PostgreSQL." },
          { name: "Rules in the database", text: "The important rules are also constraints of the database: one application per offer and candidate, one review per account, one pending appointment per application, scores from 1 to 5, consistent salary ranges, no empty message." },
        ],
      },
    },
    code: {
      title: "The code",
      text: "The source code of the site is public on GitHub, with its history.",
      link: "See the repository on GitHub",
    },
  },

  // Not-found page, for any address the router does not know
  notFound: {
    title: "Page not found",
    text: "There is nothing at this address. It may have been mistyped, or the page may have moved.",
    homeLink: "Back to the home page",
  },

  // Confirmation dialog, the question being given by the page
  dialog: {
    cancel: "Cancel",
  },

  // Messages shared by every form
  form: {
    failed: "Something went wrong. Please try again.",
    unreachable: "The server cannot be reached. Please try again later.",
    tooMany: "Too many attempts. Please wait a moment and try again.",
    passwordMismatch: "The two passwords do not match.",
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
