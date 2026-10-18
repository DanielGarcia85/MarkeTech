<!--
  frontend/src/components/LanguageSwitcher.vue

  Language selector — lets the user change the language at any time
  ───────────────────────────────────────────────────────────────────────────
  Displayed by AppHeader.vue. One segment per language, side by side, the
  current one filled in: a click on the other one switches the whole
  interface. Each segment shows the code of its language, which reads the
  same whatever the language displayed (no flags: they stand for countries,
  not languages).
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import { LOCALES, setLocale } from "../i18n";

// t translates a key; locale is the language currently displayed
const { t, locale } = useI18n();
</script>

<template>
  <nav class="switcher" :aria-label="t('language.label')">
    <!-- lang tells assistive tools how to read the code; aria-label gives
         them the full name; aria-current marks the language in use -->
    <button
      v-for="item in LOCALES"
      :key="item.code"
      type="button"
      class="segment"
      :lang="item.code"
      :aria-label="item.name"
      :aria-current="item.code === locale ? 'true' : undefined"
      :title="item.name"
      @click="setLocale(item.code)"
    >
      {{ item.code.toUpperCase() }}
    </button>
  </nav>
</template>

<style scoped>
/* The segments share one frame; the frame clips their corners */
.switcher {
  display: inline-flex;
  overflow: hidden;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
}

.segment {
  padding: 4px 10px;
  border: none;
  background: transparent;
  color: var(--mt-muted);
  font: inherit;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
}

/* A thin line between two segments */
.segment + .segment {
  border-left: 1px solid var(--mt-border);
}

.segment:hover {
  background: var(--mt-surface);
  color: var(--mt-text);
}

/* The language in use: filled in, and nothing happens on hover */
.segment[aria-current="true"] {
  background: var(--mt-blue);
  color: #ffffff;
  cursor: default;
}
</style>
