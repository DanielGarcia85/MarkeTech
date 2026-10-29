<!--
  frontend/src/pages/AboutPage.vue

  About page — what the project is, what it is built with, how it is delivered
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/about", to everyone, reached from the line in the middle
  of the header and from the technologies in the footer (decisions of
  23.10.2026). What the site does; then the technologies, by layer: the
  backend, the frontend, the data, the delivery, the operation of the
  server, the quality; last, the way to the code on GitHub. The page holds
  no text of its own: everything comes from the language files, under
  "about", so that the French and English versions have the same shape.
  The versions are written in those texts by hand: they follow
  backend/requirements.txt and frontend/package.json, and change with
  them.
-->

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import { REPOSITORY } from "../site";

// tm returns a block of the language file as it is stored, rt turns one of
// its texts into a string (as in LegalText.vue)
const { t, tm, rt } = useI18n();

type Group = { title: string; items: { name: string; text: string }[] };

// The layers of the technologies, in the order they are displayed
const GROUPS = ["backend", "frontend", "data", "delivery", "operations", "quality"] as const;

const intro = computed(() => tm("about.intro") as string[]);
const features = computed(() => tm("about.features.items") as string[]);
const groups = computed(() => GROUPS.map((key) => ({ key, ...(tm(`about.groups.${key}`) as Group) })));
</script>

<template>
  <article class="about-page">
    <h1>{{ t("about.title") }}</h1>
    <p v-for="(paragraph, i) in intro" :key="i" class="intro">{{ rt(paragraph) }}</p>

    <section>
      <h2>{{ t("about.features.title") }}</h2>
      <ul class="features">
        <li v-for="(feature, i) in features" :key="i">{{ rt(feature) }}</li>
      </ul>
    </section>

    <section>
      <h2>{{ t("about.stackTitle") }}</h2>
      <div class="groups">
        <div v-for="group in groups" :key="group.key" class="group">
          <h3>{{ rt(group.title) }}</h3>
          <dl>
            <template v-for="item in group.items" :key="rt(item.name)">
              <dt>{{ rt(item.name) }}</dt>
              <dd>{{ rt(item.text) }}</dd>
            </template>
          </dl>
        </div>
      </div>
    </section>

    <section>
      <h2>{{ t("about.code.title") }}</h2>
      <p>{{ t("about.code.text") }}</p>
      <p>
        <a :href="REPOSITORY" target="_blank" rel="noopener noreferrer" class="repository">
          {{ t("about.code.link") }}
        </a>
      </p>
    </section>
  </article>
</template>

<style scoped>
.about-page {
  max-width: 960px;
}

.intro {
  max-width: 760px;
}

h2 {
  margin: 32px 0 12px;
  color: var(--mt-blue);
  font-size: 1.35rem;
}

.features {
  max-width: 760px;
  margin: 0;
  padding-left: 20px;
}

.features li + li {
  margin-top: 4px;
}

/* The layers side by side, two by two while the width allows */
.groups {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(380px, 1fr));
  gap: 16px;
}

.group {
  padding: 16px 20px;
  border: 1px solid var(--mt-border);
  border-radius: 10px;
  background: var(--mt-surface);
}

h3 {
  margin: 0 0 10px;
  font-size: 1rem;
}

dl {
  margin: 0;
}

/* The technology in bold, what it does under it */
dt {
  font-weight: 600;
}

dd {
  margin: 0 0 10px;
  color: var(--mt-muted);
  font-size: 0.9rem;
}

dd:last-child {
  margin-bottom: 0;
}

.repository {
  font-weight: 600;
}

@media (max-width: 700px) {
  .groups {
    grid-template-columns: 1fr;
  }
}
</style>
