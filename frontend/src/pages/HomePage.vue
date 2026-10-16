<!--
  frontend/src/pages/HomePage.vue

  Home page — first page displayed when the application opens
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for the address "/". Holds for now the content
  that lived in App.vue before the router existed.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import ApiStatus from "../components/ApiStatus.vue";
import LanguageSwitcher from "../components/LanguageSwitcher.vue";

// Name of the application, displayed as the page heading
const appName: string = "MarkeTech";

// t translates a key into the language currently displayed
const { t } = useI18n();
</script>

<template>
  <h1>{{ appName }}</h1>
  <p>{{ t("app.notice") }}</p>
  <LanguageSwitcher />
  <ApiStatus />
</template>
