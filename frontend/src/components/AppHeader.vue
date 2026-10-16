<!--
  frontend/src/components/AppHeader.vue

  Header — logo, session state and language selector, on every page
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue above the current page. Shows who is logged in and
  lets them log out, or offers to sign up.
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
          {{ t("header.loggedInAs", { email: session.user.email }) }}
        </span>
        <button type="button" @click="logout">{{ t("header.logout") }}</button>
      </template>
      <RouterLink v-else :to="{ name: 'signup' }">
        {{ t("header.signup") }}
      </RouterLink>
      <LanguageSwitcher />
    </nav>
  </header>
</template>

<style scoped>
.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--mt-border);
}

.logo {
  display: block;
  height: 40px;
}

.nav {
  display: flex;
  align-items: center;
  gap: 16px;
}

.user {
  color: var(--mt-muted);
}
</style>
