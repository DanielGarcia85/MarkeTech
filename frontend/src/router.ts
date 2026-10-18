// frontend/src/router.ts
//
// Router — maps each address of the application to the page it displays
// ─────────────────────────────────────────────────────────────────────────────
// Every route is declared here, one line per page: nothing is deduced from
// the folder structure. Addresses use the browser's history (no "#" in the
// address), so the server must answer index.html for every address the
// application owns: Vite does it in development, nginx.conf in production.

import { createRouter, createWebHistory } from "vue-router";

import HomePage from "./pages/HomePage.vue";
import SignupPage from "./pages/SignupPage.vue";
import LoginPage from "./pages/LoginPage.vue";
import VerifyEmailPage from "./pages/VerifyEmailPage.vue";
import NewPasswordPage from "./pages/NewPasswordPage.vue";
import PasswordResetPage from "./pages/PasswordResetPage.vue";
import PrivacyPage from "./pages/PrivacyPage.vue";
import ProfilePage from "./pages/ProfilePage.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    // Each route has a name, used by links and redirections instead of the
    // raw address, so that an address can change in one place only
    { path: "/", name: "home", component: HomePage },
    { path: "/account/signup", name: "signup", component: SignupPage },
    { path: "/account/login", name: "login", component: LoginPage },
    { path: "/account/verify-email/:key", name: "verifyEmail", component: VerifyEmailPage,},
    { path: "/account/password/reset", name: "passwordReset", component: PasswordResetPage },
    { path: "/account/password/reset/:key", name: "newPassword", component: NewPasswordPage },
    { path: "/privacy", name: "privacy", component: PrivacyPage },
    { path: "/account/profile", name: "profile", component: ProfilePage },
  ],
});
