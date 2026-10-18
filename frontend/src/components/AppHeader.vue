<!--
  frontend/src/components/AppHeader.vue

  Header — logo, session state and language selector, on every page
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue above the current page. Shows who is logged in and
  lets them log out, or offers to sign up and to log in.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import logoUrl from "../assets/logo-horizontal.svg";
import { logout, useSession } from "../session";
import LanguageSwitcher from "./LanguageSwitcher.vue";

const { t } = useI18n();

// Read-only view of the session: updated by session.ts when it changes
const session = useSession();
</script>

<template>
  <header class="header">
    <RouterLink :to="{ name: 'home' }">
      <img :src="logoUrl" alt="MarkeTech" class="logo" />
    </RouterLink>
    <nav class="nav">
      <template v-if="session.user">
        <span class="user">
          {{ t("header.loggedInAs", { name: session.user.display }) }}
        </span>
        <button type="button" class="as-link" @click="logout">
          {{ t("header.logout") }}
        </button>
      </template>
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
   the links go under the logo rather than past the edge of the window */
.header {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 8px 16px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--mt-border);
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

.user {
  color: var(--mt-muted);
}
</style>
