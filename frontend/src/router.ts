// frontend/src/router.ts
//
// Router — maps each address of the application to the page it displays
// ─────────────────────────────────────────────────────────────────────────────
// Every route is declared here, one line per page: nothing is deduced from
// the folder structure. Addresses use the browser's history (no "#" in the
// address), so the server must answer index.html for every address the
// application owns: Vite does it in development, nginx.conf in production.
// A route may be reserved to users (requiresAuth) or to visitors
// (guestOnly): the guard at the end sends the others away before the page
// is shown.

import { createRouter, createWebHistory } from "vue-router";

import HomePage from "./pages/HomePage.vue";
import SignupPage from "./pages/SignupPage.vue";
import LoginPage from "./pages/LoginPage.vue";
import VerifyEmailPage from "./pages/VerifyEmailPage.vue";
import NewPasswordPage from "./pages/NewPasswordPage.vue";
import PasswordResetPage from "./pages/PasswordResetPage.vue";
import PrivacyPage from "./pages/PrivacyPage.vue";
import ProfilePage from "./pages/ProfilePage.vue";
import NotFoundPage from "./pages/NotFoundPage.vue";
import { useSession, whenLoaded } from "./session";

// What a route may ask for, read by the guard below. Declared to the
// router's own types, so that a misspelled key is a type error
declare module "vue-router" {
  interface RouteMeta {
    requiresAuth?: boolean;
    guestOnly?: boolean;
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
    { path: "/privacy", name: "privacy", component: PrivacyPage },
    // Any other address: the "not found" page, the address left as typed
    { path: "/:pathMatch(.*)*", name: "notFound", component: NotFoundPage },
  ],
});

// Before each navigation: a page for users sends a visitor to the login
// page, a page for visitors sends a user to the home page. Waits for the
// session to be known first, so that a reload on a user's page does not
// bounce while the backend is being asked
const session = useSession();

router.beforeEach(async (to) => {
  if (!to.meta.requiresAuth && !to.meta.guestOnly) return true;
  await whenLoaded();
  if (to.meta.requiresAuth && !session.user) return { name: "login" };
  if (to.meta.guestOnly && session.user) return { name: "home" };
  return true;
});
