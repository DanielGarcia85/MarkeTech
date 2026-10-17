<!--
  frontend/src/App.vue

  Root component — top of the component tree, and the page shell
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Asks the backend who is logged in, then lays out the
  three bands of every page: the header, the body (the current page, with
  room for the side bar of a later slice) and the footer. The body stretches
  so that the footer stays at the bottom of the window, even on a short page.
  Every page is declared in router.ts.
-->

<script setup lang="ts">
import AppHeader from "./components/AppHeader.vue";
import { loadSession } from "./session";

// Runs once, when the application starts
loadSession();
</script>

<template>
  <div class="shell">
    <AppHeader />
    <div class="body">
      <!-- The side bar of the navigation goes here, before the page -->
      <main class="page">
        <RouterView />
      </main>
    </div>
    <!-- The footer goes here, after the body -->
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
</style>
