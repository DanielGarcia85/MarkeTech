<!--
  frontend/src/pages/PrivacyPage.vue

  Privacy page — what the site does with the data of its users
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/privacy", reached from the footer. The page holds no text
  of its own: every section comes from the language files, in the order
  fixed here, so that the French and English versions have the same shape.
-->

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { CONTACT } from "../site";

// t translates one key. tm returns a whole block of the language file as it
// is stored, and rt turns one text of that block into a string, as t does
// for a key: together they read a list of texts without naming each key
const { t, tm, rt } = useI18n();

// The sections of the page, in the order they are displayed. Each one is a
// key of "privacy.sections" in the language files
const SECTION_KEYS = [
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

// Shape of a section in the language files: a title and opening paragraphs;
// some sections add a list of terms with their text, and closing paragraphs
type Section = {
  title: string;
  intro: string[];
  items?: { term: string; text: string }[];
  outro?: string[];
};

// The sections, read in the language currently displayed; read again when
// the language changes
const sections = computed(() =>
  SECTION_KEYS.map((key) => tm(`privacy.sections.${key}`) as Section),
);

// A text of a section, with the contact address put where the text says
// "{contact}": an "@" cannot be written in a translation, where it has a
// meaning of its own
function text(message: string): string {
  return rt(message, { contact: CONTACT });
}
</script>

<template>
  <article class="privacy">
    <h1>{{ t("privacy.title") }}</h1>
    <p class="updated">{{ t("privacy.updated") }}</p>

    <section v-for="section in sections" :key="rt(section.title)">
      <h2>{{ rt(section.title) }}</h2>
      <p v-for="(message, i) in section.intro" :key="i">{{ text(message) }}</p>
      <dl v-if="section.items" class="items">
        <template v-for="item in section.items" :key="rt(item.term)">
          <dt>{{ rt(item.term) }}</dt>
          <dd>{{ text(item.text) }}</dd>
        </template>
      </dl>
      <p v-for="(message, i) in section.outro" :key="i">{{ text(message) }}</p>
    </section>
  </article>
</template>

<style scoped>
/* A column of text narrower than the page: long lines read badly */
.privacy {
  max-width: 720px;
}

.updated {
  margin-top: -8px;
  color: var(--mt-muted);
}

h2 {
  margin: 28px 0 8px;
  font-size: 1.15rem;
}

/* Each term in bold, its text under it, without the indent browsers add */
.items {
  margin: 0;
}

.items dt {
  margin-top: 8px;
  font-weight: 600;
}

.items dd {
  margin: 0;
}
</style>
