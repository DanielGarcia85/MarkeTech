<!--
  frontend/src/pages/PrivacyPage.vue

  Privacy page — what the site does with the data of its users
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/privacy", reached from the footer and from the sign-up
  page. The page holds no text of its own: every section comes from the
  language files, under "privacy", in the order fixed here (LegalText.vue
  does the reading).
-->

<script setup lang="ts">
import LegalText from "../components/LegalText.vue";

// The sections of the page, in the order they are displayed
const SECTIONS = [
  "controller",
  "data",
  "cookies",
  "emails",
  "hosting",
  "retention",
  "security",
  "rights",
  "changes",
] as const;
</script>

<template>
  <LegalText root="privacy" :sections="SECTIONS" />
</template>
