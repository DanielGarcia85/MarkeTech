<!--
  frontend/src/App.vue

  Root component — top of the component tree, and the page shell
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Asks the backend who is logged in, then lays out the
  three bands of every page: the header, the body (the side bar, the
  current page, then the reviews on a wide window) and the footer, plus the
  confirmation dialog that any page may open. The body stretches so that
  the footer stays at the bottom of the window, even on a short page. A
  demo account sees a band under the header (shared, made again every
  night), kept at the top of the window with it. Every page is declared
  in router.ts.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import AppFooter from "./components/AppFooter.vue";
import AppHeader from "./components/AppHeader.vue";
import AppSidebar from "./components/AppSidebar.vue";
import ConfirmDialog from "./components/ConfirmDialog.vue";
import ReviewsAside from "./components/ReviewsAside.vue";
import { loadSession, useSession } from "./session";

const { t } = useI18n();
const session = useSession();
const route = useRoute();

// Runs once, when the application starts
loadSession();
</script>

<template>
  <div class="shell">
    <!-- The header and the band of a demo account stay at the top of the
         window together while the page scrolls -->
    <div class="top">
      <AppHeader />
      <p v-if="session.user?.is_demo" class="demo-band">{{ t("demo.band") }}</p>
    </div>
    <div class="body">
      <!-- The navigation, before the page: the offers for everyone, more
           for a logged-in user -->
      <AppSidebar />
      <main class="page">
        <RouterView />
      </main>
      <!-- The reviews of the platform, on a wide window, on every page but
           their own list -->
      <ReviewsAside v-if="route.name !== 'reviews'" />
    </div>
    <AppFooter />
    <!-- Invisible until a page asks a question -->
    <ConfirmDialog />
  </div>
</template>

<style scoped>
/* The header and the band, fixed together at the top of the window while
   the page scrolls under them: drawn above the page */
.top {
  position: sticky;
  top: 0;
  z-index: 10;
}

/* A demo account: a thin band of the accent under the header */
.demo-band {
  margin: 0;
  padding: 6px 16px;
  border-bottom: 1px solid var(--mt-accent);
  background: var(--mt-accent-surface);
  color: var(--mt-accent-dark);
  font-size: 0.9rem;
  font-weight: 500;
  text-align: center;
}

/* The whole window, as a column: header, body, footer */
.shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

/* The body takes all the height left by the header and the footer */
.body {
  display: flex;
  flex: 1;
}

/* The page takes all the width left by the side bar */
.page {
  flex: 1;
  min-width: 0;
}

/* Narrow window: the side bar becomes a strip above the page */
@media (max-width: 900px) {
  .body {
    flex-direction: column;
  }
}
</style>
