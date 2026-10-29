<!--
  frontend/src/pages/PrivacyPage.vue

  Privacy page — what the site does with the data of its users
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/privacy", reached from the footer and from the sign-up
  page. The page holds no text of its own: every section comes from the
  language files, under "privacy", in the order fixed here (LegalText.vue
  does the reading). It follows the Swiss Federal Act on Data Protection
  and, for visitors in the European Union, the GDPR.
-->

<script setup lang="ts">
import LegalText from "../components/LegalText.vue";

// The sections of the page, in the order they are displayed; the first one,
// the summary, is set apart in a box
const SECTIONS = [
  "summary",
  "controller",
  "data",
  "bases",
  "recipients",
  "abroad",
  "retention",
  "cookies",
  "security",
  "rights",
  "automated",
  "changes",
] as const;
</script>

<template>
  <LegalText root="privacy" :sections="SECTIONS" highlight="summary" />
</template>
