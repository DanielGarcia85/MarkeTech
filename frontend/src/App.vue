<!--
  frontend/src/App.vue

  Root component — top of the component tree
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Every other component is displayed inside this one.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import ApiStatus from "./components/ApiStatus.vue";
import LanguageSwitcher from "./components/LanguageSwitcher.vue";

// Name of the application, displayed as the page heading
const appName: string = "MarkeTech";

// t translates a key into the language currently displayed
const { t } = useI18n();
</script>

<template>
  <main>
    <h1>{{ appName }}</h1>
    <p>{{ t("app.notice") }}</p>
    <LanguageSwitcher />
    <ApiStatus />
  </main>
</template>
