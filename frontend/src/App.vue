<!--
  frontend/src/App.vue

  Root component — top of the component tree
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Every other component is displayed inside this one.
-->

<script setup lang="ts">
// Name of the application, displayed as the page heading
const appName: string = "MarkeTech";
</script>

<template>
  <main>
    <h1>{{ appName }}</h1>
  </main>
</template>
