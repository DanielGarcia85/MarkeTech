<!--
  frontend/src/components/LegalText.vue

  Legal text — a page of sections read from the language files
  ───────────────────────────────────────────────────────────────────────────
  Used by the privacy page and by the terms of use: the component holds no
  text of its own. It is given the root key of the page ("privacy", "terms")
  and the keys of its sections, in the order to display them, so that the
  French and English versions have the same shape. A section has a title
  and opening paragraphs; some add a list of terms with their text, and
  closing paragraphs. The contact address goes where a text says {contact}.
-->

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { CONTACT } from "../site";

const props = defineProps<{
  // The key of the page in the language files: its title, its date, its sections
  root: string;
  // The sections to show, in this order: keys of "<root>.sections"
  sections: readonly string[];
}>();

// t translates one key. tm returns a whole block of the language file as it
// is stored, and rt turns one text of that block into a string, as t does
// for a key: together they read a list of texts without naming each key
const { t, tm, rt } = useI18n();

type Section = {
  title: string;
  intro: string[];
  items?: { term: string; text: string }[];
  outro?: string[];
};

// The sections, read in the language currently displayed; read again when
// the language changes
const blocks = computed(() => props.sections.map((key) => tm(`${props.root}.sections.${key}`) as Section));

// A text of a section, with the contact address put where the text says
// "{contact}": an "@" cannot be written in a translation, where it has a
// meaning of its own
function text(message: string): string {
  return rt(message, { contact: CONTACT });
}
</script>

<template>
  <article class="legal">
    <h1>{{ t(`${root}.title`) }}</h1>
    <p class="updated">{{ t(`${root}.updated`) }}</p>

    <section v-for="section in blocks" :key="rt(section.title)">
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
.legal {
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

/* Both edges straight on a wide screen, where the lines are long enough;
   ragged on the right under 721 px, where justifying opens rivers */
.legal p,
.legal dd {
  hyphens: auto;
}

@media (min-width: 721px) {
  .legal p,
  .legal dd {
    text-align: justify;
  }
}
</style>
