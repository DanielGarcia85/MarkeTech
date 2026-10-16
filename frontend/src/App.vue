<!--
  frontend/src/App.vue

  Root component — top of the component tree
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Asks the backend who is logged in, then displays the
  page that matches the current address; every page is declared in router.ts.
-->

<script setup lang="ts">
import { loadSession } from "./session";

// Runs once, when the application starts
loadSession();
</script>

<template>
  <main>
    <RouterView />
  </main>
</template>
