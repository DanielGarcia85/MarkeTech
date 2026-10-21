<!--
  frontend/src/App.vue

  Root component — top of the component tree, and the page shell
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Asks the backend who is logged in, then lays out the
  three bands of every page: the header, the body (the side bar, then the
  current page) and the footer, plus the
  confirmation dialog that any page may open. The body stretches so that
  the footer stays at the bottom of the window, even on a short page.
  Every page is declared in router.ts.
-->

<script setup lang="ts">
import AppFooter from "./components/AppFooter.vue";
import AppHeader from "./components/AppHeader.vue";
import AppSidebar from "./components/AppSidebar.vue";
import ConfirmDialog from "./components/ConfirmDialog.vue";
import { loadSession } from "./session";

// Runs once, when the application starts
loadSession();
</script>

<template>
  <div class="shell">
    <AppHeader />
    <div class="body">
      <!-- The navigation, before the page: the offers for everyone, more
           for a logged-in user -->
      <AppSidebar />
      <main class="page">
        <RouterView />
      </main>
    </div>
    <AppFooter />
    <!-- Invisible until a page asks a question -->
    <ConfirmDialog />
  </div>
</template>

<style scoped>
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
