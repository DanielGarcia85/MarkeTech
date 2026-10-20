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

  // The two roles, as shown to the logged-in user (header menu, profile)
  roles: {
    candidate: "Candidate",
    employer: "Employer",
  },

  // Header: session state and links of the account
  header: {
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
    account: "My account",
    profile: "Profile",
  },

  // Footer: who is behind the site, where to find more, how to get in touch
  footer: {
    about: "MarkeTech is a demonstration project, without commercial activity,\nrewritten by Daniel Garcia from a team project of HEG Genève.",
    github: "GitHub",
    linkedin: "LinkedIn",
    portfolio: "Portfolio",
    contact: "Contact",
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
    invalidLoggedIn: "This link is invalid or has expired. Your current address stays in force; you can ask again from your profile.",
    loginLink: "Log in",
    profileLink: "Back to my profile",
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
    updated: "Last updated: 19 October 2026",
    sections: {
      controller: {
        title: "Who is responsible",
        intro: [
          "MarkeTech is a demonstration project, without commercial activity: a job board for students and young graduates in computer science, built by Daniel Garcia to show his work. It works like a real platform, but nobody gets hired through it.",
          "The person responsible for the processing of your data is Daniel Garcia, Geneva, Switzerland. For any question about this page or about your data, write to {contact}.",
          "The site is there to be tried out. You do not need real documents to do so, and nothing you enter is used for anything else than running the site.",
        ],
      },
      data: {
        title: "Data processed",
        intro: ["The site only stores what its features need. Depending on what you do, that is:"],
        items: [
          { term: "Account", text: "E-mail address, password (stored hashed, never readable), first name, last name, role (candidate or employer), whether the address is verified, dates of sign-up and of last login." },
          { term: "Candidate profile", text: "Postal address, phone number, photo, CV and any other document you attach." },
          { term: "Employer profile", text: "Postal address, phone number, photo, and the company: name, address, phone number, logo." },
          { term: "Job offers", text: "Title, description, location, salary range, years of experience required, company name and logo, date of publication. Offers are visible to every visitor of the site." },
          { term: "Applications", text: "The offer applied to, the CV and cover letter submitted, the date, the status (received, in progress, accepted, rejected) and its history. An application is seen by the candidate and by the employer who published the offer." },
          { term: "Messages", text: "Exchanged between a candidate and an employer about an application: subject, text, dates. Only the two of them can read them." },
          { term: "Favourites", text: "The offers a candidate has set aside." },
          { term: "Appointments", text: "Proposed by an employer about an application: date and time, description, the candidate's answer and the message that goes with it." },
          { term: "Reviews of the platform", text: "An overall rating, four detailed ratings and a comment, published with your first name and last name, visible to every visitor." },
          { term: "Technical data", text: "The server logs the requests it receives: IP address, page requested, date, browser. These logs serve for security and troubleshooting only, and are erased automatically as newer ones replace them." },
        ],
        outro: [
          "The administrator of the site sees all this data in its administration interface, to run the site and to answer your requests. Nothing else is collected: no profiling, no advertising, no audience measurement.",
        ],
      },
      cookies: {
        title: "Cookies and local storage",
        intro: ["The site sets no third-party cookie and uses no tracker. It only keeps in your browser what it needs to work:"],
        items: [
          { term: "sessionid", text: "A cookie that keeps you logged in; it lasts two weeks at most and is deleted when you log out." },
          { term: "csrftoken", text: "A cookie that protects the forms against requests forged by another site; it lasts one year." },
          { term: "marketech.locale", text: "The language you chose, kept in the local storage of your browser until you clear it." },
        ],
      },
      emails: {
        title: "E-mails",
        intro: ["The site writes to you about your account only: to verify your address when you sign up, and to send you a link when you forget your password. No newsletter, no advertising. The e-mails leave through the mail service of Infomaniak."],
      },
      hosting: {
        title: "Hosting and sharing",
        intro: [
          "The site runs on a server rented from Infomaniak, in Switzerland, and its data stays in Switzerland. Infomaniak hosts the server, keeps its backup copies and sends its e-mails; it is the only company that handles data on behalf of the site.",
          "The source code of the site is public on GitHub and contains no personal data. No data is sold, rented or passed on to anyone else. Within the site, your data is only shown to the people its features imply: an employer sees the applications to its offers, a candidate sees the company behind an offer, and reviews are public.",
        ],
      },
      retention: {
        title: "How long data is kept",
        intro: [
          "Your data is kept as long as your account exists. What you delete yourself, an offer, a favourite, a document, disappears at once. When your account is deleted, everything attached to it goes with it: profile, offers, applications, messages, appointments, favourites and review.",
          "To have your account deleted, write to {contact} from the address of the account. The server logs are erased automatically, as said above.",
        ],
      },
      security: {
        title: "Security",
        intro: ["The whole site is served over HTTPS. Passwords are stored hashed, never in clear. The photos and the documents you upload (CV, letters, other documents) are private: the site checks who asks for them before handing them over, and no address leads to them directly; only the logo of the company is public, since it goes with the job offers. Access to the server itself is reserved to its administrator."],
      },
      rights: {
        title: "Your rights",
        intro: [
          "Under the Swiss Federal Act on Data Protection (FADP), you can ask what data the site holds about you, have it corrected or deleted, and object to its processing. A message to {contact} is enough: the answer is free of charge and comes, as a rule, within 30 days. You can also change most of your data yourself, from your account.",
          "If you think your rights are not respected, you can turn to the Federal Data Protection and Information Commissioner (FDPIC).",
        ],
      },
      changes: {
        title: "Changes to this page",
        intro: ["This page describes the site as it is. It changes when the site changes, and the date at the top says when it was last updated."],
      },
    },
  },

  // Profile page: names and contact details, company, files and documents,
  // then the account: e-mail address and password
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
    account: "Account",
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
    back: "All offers",
    notFound: "This offer does not exist, or is no longer published.",
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
    needsCompany: "Give the name of your company in your profile before publishing.",
    companyLink: "Complete my profile",
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
