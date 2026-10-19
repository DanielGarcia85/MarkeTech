<!--
  frontend/src/components/AppHeader.vue

  Header — logo, account menu and language selector, on every page
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue above the current page, and kept at the top of the
  window while the page scrolls. A logged-in user is shown as a round with
  their initials, which opens a small menu: their name, the profile, the
  way to log out. A visitor gets the links to sign up and to log in.
-->

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRouter } from "vue-router";

import logoUrl from "../assets/logo-horizontal.svg";
import { logout, useSession } from "../session";
import LanguageSwitcher from "./LanguageSwitcher.vue";

const { t } = useI18n();
const router = useRouter();

// Read-only view of the session: updated by session.ts when it changes
const session = useSession();

// The letters in the round: the initials of the first and last words of
// the name, or the first two letters of what is displayed (the address,
// for an account without names)
const initials = computed(() => {
  const display = session.user?.display ?? "";
  const words = display.split(/\s+/).filter((word) => word.length > 0);
  const first = words[0] ?? "";
  const last = words.length > 1 ? (words[words.length - 1] ?? "") : "";
  return (last ? first.charAt(0) + last.charAt(0) : first.slice(0, 2)).toUpperCase();
});

// ── The account menu ──────────────────────────────────────────────────

// Whether the menu is open, and the element that holds the round and the
// menu, to tell a click inside from a click outside
const open = ref(false);
const account = ref<HTMLElement | null>(null);

// A click anywhere outside the menu closes it; so does the Escape key
function closeOnClickOutside(event: MouseEvent): void {
  if (open.value && account.value && !account.value.contains(event.target as Node)) {
    open.value = false;
  }
}

function closeOnEscape(event: KeyboardEvent): void {
  if (event.key === "Escape") open.value = false;
}

// The listeners live as long as the header does: added when it appears,
// removed when it leaves (the header never leaves, but the rule holds)
onMounted(() => {
  document.addEventListener("click", closeOnClickOutside);
  document.addEventListener("keydown", closeOnEscape);
});

onUnmounted(() => {
  document.removeEventListener("click", closeOnClickOutside);
  document.removeEventListener("keydown", closeOnEscape);
});

// Logs out, then shows the home page: the page left may be for users only
async function leave(): Promise<void> {
  open.value = false;
  await logout();
  router.push({ name: "home" });
}
</script>

<template>
  <header class="header">
    <RouterLink :to="{ name: 'home' }">
      <img :src="logoUrl" alt="MarkeTech" class="logo" />
    </RouterLink>
    <nav class="nav">
      <div v-if="session.user" ref="account" class="account">
        <!-- The round opens and closes the menu -->
        <button
          type="button"
          class="avatar"
          :title="session.user.display"
          :aria-label="t('header.account')"
          aria-haspopup="menu"
          :aria-expanded="open"
          @click="open = !open"
        >
          {{ initials }}
        </button>
        <div v-if="open" class="menu" role="menu">
          <p class="who">{{ session.user.display }}</p>
          <RouterLink :to="{ name: 'profile' }" role="menuitem" @click="open = false">
            {{ t("header.profile") }}
          </RouterLink>
          <button type="button" role="menuitem" @click="leave">
            {{ t("header.logout") }}
          </button>
        </div>
      </div>
      <template v-else>
        <RouterLink :to="{ name: 'signup' }">{{ t("header.signup") }}</RouterLink>
        <RouterLink :to="{ name: 'login' }">{{ t("header.login") }}</RouterLink>
      </template>
      <LanguageSwitcher />
    </nav>
  </header>
</template>

<style scoped>
/* The logo on the left, the links on the right. When the width runs out,
   the links go under the logo rather than past the edge of the window.
   Stays at the top of the window while the page scrolls under it: it
   needs its own background, and to be drawn above the page */
.header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 16px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--mt-border);
  background: var(--mt-background);
}

.logo {
  display: block;
  height: 40px;
}

/* Kept on the right, on its own line too; its own items wrap if needed,
   and stay on the right as well */
.nav {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 8px 16px;
  margin-left: auto;
}

/* The round and its menu: the menu is placed from the round */
.account {
  position: relative;
}

/* A round with the initials; the name shows as a tooltip. Darker on
   hover, like the main buttons */
.avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: none;
  border-radius: 50%;
  background: var(--mt-blue);
  color: #ffffff;
  font: inherit;
  font-size: 0.8rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  cursor: pointer;
}

.avatar:hover,
.avatar[aria-expanded="true"] {
  background: var(--mt-blue-dark);
}

/* The menu hangs under the round, aligned on its right edge, above the
   page */
.menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  z-index: 20;
  min-width: 200px;
  padding: 6px 0;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-background);
  box-shadow: 0 8px 24px rgba(30, 41, 59, 0.12);
}

/* The name of the account, at the top of the menu, not clickable */
.who {
  margin: 0;
  padding: 6px 14px 8px;
  border-bottom: 1px solid var(--mt-border);
  color: var(--mt-muted);
  font-size: 0.85rem;
  white-space: nowrap;
}

/* One entry per line, link or button alike */
.menu a,
.menu button {
  display: block;
  width: 100%;
  padding: 8px 14px;
  border: none;
  background: none;
  color: var(--mt-text);
  font: inherit;
  text-align: left;
  text-decoration: none;
  white-space: nowrap;
  cursor: pointer;
}

.menu a:hover,
.menu button:hover {
  background: var(--mt-surface);
}
</style>
