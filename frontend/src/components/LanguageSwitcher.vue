<!--
  frontend/src/components/LanguageSwitcher.vue

  Language selector — lets the user change the language at any time
  ───────────────────────────────────────────────────────────────────────────
  Lists the available languages and applies the one that is picked.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import { LOCALES, setLocale, type Locale } from "../i18n";

// t translates a key; locale is the language currently displayed
const { t, locale } = useI18n();

// Called each time the user picks a language in the list
function onChange(event: Event): void {
  const select = event.target as HTMLSelectElement;
  setLocale(select.value as Locale);
}
</script>

<template>
  <label>
    {{ t("language.label") }}
    <select :value="locale" @change="onChange">
      <option v-for="item in LOCALES" :key="item.code" :value="item.code">
        {{ item.name }}
      </option>
    </select>
  </label>
</template>
