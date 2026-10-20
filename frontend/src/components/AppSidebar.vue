<!--
  frontend/src/components/AppSidebar.vue

  Side bar — the navigation of a logged-in user, on every page
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue on the left of the page, for a logged-in user only.
  One group of links per area of the application; a group gets its links
  when the pages exist, never before, and a link of one role shows for that
  role only. On a narrow window, the bar becomes a strip under the header.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import { useSession } from "../session";

const { t } = useI18n();
const session = useSession();
</script>

<template>
  <nav class="sidebar" :aria-label="t('nav.label')">
    <p class="group">{{ t("nav.offers") }}</p>
    <RouterLink :to="{ name: 'home' }">{{ t("nav.allOffers") }}</RouterLink>
    <RouterLink v-if="session.user?.role === 'employer'" :to="{ name: 'myOffers' }">
      {{ t("nav.myOffers") }}
    </RouterLink>
    <p class="group">{{ t("nav.account") }}</p>
    <RouterLink :to="{ name: 'profile' }">{{ t("nav.profile") }}</RouterLink>
  </nav>
</template>

<style scoped>
.sidebar {
  flex: none;
  width: 220px;
  padding: 20px 12px;
  border-right: 1px solid var(--mt-border);
  background: var(--mt-surface);
}

/* The title of a group of links: small capitals, muted */
.group {
  margin: 0 10px 6px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--mt-muted);
}

/* A gap above every group but the first */
.sidebar a + .group {
  margin-top: 20px;
}

/* One link per line; the page being shown is marked by the router with
   the class router-link-active */
.sidebar a {
  display: block;
  padding: 8px 10px;
  border-radius: 6px;
  color: var(--mt-text);
  text-decoration: none;
}

.sidebar a:hover {
  background: var(--mt-border);
}

.sidebar a.router-link-active {
  background: var(--mt-blue);
  color: #ffffff;
}

/* Narrow window: a strip under the header, the links side by side */
@media (max-width: 900px) {
  .sidebar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 8px;
    width: auto;
    padding: 8px 16px;
    border-right: none;
    border-bottom: 1px solid var(--mt-border);
  }

  .group {
    margin: 0 8px 0 0;
  }

  .sidebar a {
    padding: 6px 10px;
  }
}
</style>
