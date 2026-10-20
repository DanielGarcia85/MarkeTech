<!--
  frontend/src/pages/TermsPage.vue

  Terms page — the terms of use accepted at sign-up
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/terms", reached from the footer and from the sign-up page,
  where a visitor must accept these terms to create an account. The page
  holds no text of its own: every section comes from the language files,
  under "terms", in the order fixed here (LegalText.vue does the reading).
-->

<script setup lang="ts">
import LegalText from "../components/LegalText.vue";

// The sections of the page, in the order they are displayed
const SECTIONS = ["purpose", "account", "use", "content", "availability", "data", "law", "changes"] as const;
</script>

<template>
  <LegalText root="terms" :sections="SECTIONS" />
</template>
