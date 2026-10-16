<!--
  frontend/src/App.vue

  Root component — top of the component tree
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Displays the page that matches the current address;
  every page is declared in router.ts.
-->

<template>
  <main>
    <RouterView />
  </main>
</template>
