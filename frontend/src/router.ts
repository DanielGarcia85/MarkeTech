// frontend/src/router.ts
//
// Router — maps each address of the application to the page it displays
// ─────────────────────────────────────────────────────────────────────────────
// Every route is declared here, one line per page: nothing is deduced from
// the folder structure. Addresses use the browser's history (no "#" in the
// address), so the server must answer index.html for every address the
// application owns: Vite does it in development, nginx.conf in production.
// A route may be reserved to users (requiresAuth), to visitors (guestOnly)
// or to one role (requiresRole): the guard at the end sends the others
// away before the page is shown. A visitor sent to the login page comes
// back to the page asked for once logged in (?next=, read by LoginPage).

import { createRouter, createWebHistory } from "vue-router";

import HomePage from "./pages/HomePage.vue";
import SignupPage from "./pages/SignupPage.vue";
import LoginPage from "./pages/LoginPage.vue";
import VerifyEmailPage from "./pages/VerifyEmailPage.vue";
import NewPasswordPage from "./pages/NewPasswordPage.vue";
import PasswordResetPage from "./pages/PasswordResetPage.vue";
import PrivacyPage from "./pages/PrivacyPage.vue";
import TermsPage from "./pages/TermsPage.vue";
import ProfilePage from "./pages/ProfilePage.vue";
import OfferPage from "./pages/OfferPage.vue";
import MyOffersPage from "./pages/MyOffersPage.vue";
import OfferFormPage from "./pages/OfferFormPage.vue";
import OfferApplicationsPage from "./pages/OfferApplicationsPage.vue";
import ReceivedApplicationsPage from "./pages/ReceivedApplicationsPage.vue";
import ApplyPage from "./pages/ApplyPage.vue";
import MyApplicationsPage from "./pages/MyApplicationsPage.vue";
import MyFavoritesPage from "./pages/MyFavoritesPage.vue";
import NotFoundPage from "./pages/NotFoundPage.vue";
import type { Role } from "./api/account";
import { useSession, whenLoaded } from "./session";

// What a route may ask for, read by the guard below. Declared to the
// router's own types, so that a misspelled key is a type error
declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
    // A page of one role only: a user of the other role is sent home
    requiresRole?: Role;
  }
}

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Each route has a name, used by links and redirections instead of the
    // raw address, so that an address can change in one place only
    { path: "/", name: "home", component: HomePage },
    { path: "/account/signup", name: "signup", component: SignupPage, meta: { guestOnly: true } },
    { path: "/account/login", name: "login", component: LoginPage, meta: { guestOnly: true } },
    { path: "/account/verify-email/:key", name: "verifyEmail", component: VerifyEmailPage },
    { path: "/account/password/reset", name: "passwordReset", component: PasswordResetPage },
    { path: "/account/password/reset/:key", name: "newPassword", component: NewPasswordPage },
    { path: "/account/profile", name: "profile", component: ProfilePage, meta: { requiresAuth: true } },
    // The job offers: the list is the home page; one offer by its number
    { path: "/offers", redirect: (to) => ({ name: "home", query: to.query }) },
    { path: "/offers/:id(\\d+)", name: "offer", component: OfferPage },
    // Applying to an offer, and the applications of a candidate
    { path: "/offers/:id(\\d+)/apply", name: "apply", component: ApplyPage, meta: { requiresRole: "candidate" } },
    { path: "/candidate/applications", name: "myApplications", component: MyApplicationsPage, meta: { requiresRole: "candidate" } },
    // The offers a candidate put aside
    { path: "/candidate/favorites", name: "myFavorites", component: MyFavoritesPage, meta: { requiresRole: "candidate" } },
    // The offers of an employer: their list, a new one, one to change
    { path: "/employer/offers", name: "myOffers", component: MyOffersPage, meta: { requiresRole: "employer" } },
    { path: "/employer/offers/new", name: "offerNew", component: OfferFormPage, meta: { requiresRole: "employer" } },
    { path: "/employer/offers/:id(\\d+)/edit", name: "offerEdit", component: OfferFormPage, meta: { requiresRole: "employer" } },
    { path: "/employer/offers/:id(\\d+)/applications", name: "offerApplications", component: OfferApplicationsPage, meta: { requiresRole: "employer" } },
    // All the applications received by an employer, whatever the offer
    { path: "/employer/applications", name: "receivedApplications", component: ReceivedApplicationsPage, meta: { requiresRole: "employer" } },
    { path: "/privacy", name: "privacy", component: PrivacyPage },
    { path: "/terms", name: "terms", component: TermsPage },
    // Any other address: the "not found" page, the address left as typed
    { path: "/:pathMatch(.*)*", name: "notFound", component: NotFoundPage },
  ],
});

// Before each navigation: a page for users sends a visitor to the login
// page, with the address asked for to come back to; a page for visitors
// sends a user to the home page, a page of one role sends the other role to
// the home page. Waits for the session to be known first, so that a reload
// on a user's page does not bounce while the backend is being asked
const session = useSession();

router.beforeEach(async (to) => {
  const { requiresAuth, guestOnly, requiresRole } = to.meta;
  if (!requiresAuth && !guestOnly && !requiresRole) return true;
  await whenLoaded();
  if ((requiresAuth || requiresRole) && !session.user) return { name: "login", query: { next: to.fullPath } };
  if (guestOnly && session.user) return { name: "home" };
  if (requiresRole && session.user?.role !== requiresRole) return { name: "home" };
  return true;
});
