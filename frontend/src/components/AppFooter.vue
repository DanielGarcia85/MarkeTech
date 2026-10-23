<!--
  frontend/src/components/AppFooter.vue

  Footer — who is behind the site, where to find more, how to get in touch
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue under the current page. One band across the whole
  width, in the dark blue with light text, under a thin line in the accent
  colour: a sentence on the left, the links on two rows in the centre, the
  privacy link above the copyright on the right; under a thin line, across
  the whole width, the technologies of the site with the way to the about
  page, and whether the backend answers (ApiStatus, decisions of
  23.10.2026).
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import { CONTACT } from "../site";
import ApiStatus from "./ApiStatus.vue";

const { t } = useI18n();

// Each link: where it leads, and whose profile it is (shown next to the
// translated label, so that the visitor knows who is behind it)
const LINKS = [
  { key: "github", who: "DanielGarcia85", href: "https://github.com/DanielGarcia85" },
  { key: "linkedin", who: "Daniel Garcia", href: "https://www.linkedin.com/in/danielgarcia85/" },
  { key: "portfolio", who: "danielgarcia.it", href: "https://danielgarcia.it" },
] as const;

// Year of the copyright line, taken from the clock of the browser
const year = new Date().getFullYear();
</script>

<template>
  <footer class="footer">
    <p class="about">{{ t("footer.about") }}</p>
    <ul class="links">
      <li v-for="link in LINKS" :key="link.key">
        <a :href="link.href" target="_blank" rel="noopener noreferrer">
          {{ t(`footer.${link.key}`) }}
          <span class="who">{{ link.who }}</span>
        </a>
      </li>
      <li>
        <a :href="`mailto:${CONTACT}`">
          {{ t("footer.contact") }}
          <span class="who">{{ CONTACT }}</span>
        </a>
      </li>
    </ul>
    <p class="legal">
      <span class="pages">
        <RouterLink :to="{ name: 'terms' }">{{ t("footer.terms") }}</RouterLink>
        ·
        <RouterLink :to="{ name: 'privacy' }">{{ t("footer.privacy") }}</RouterLink>
      </span>
      <span>{{ t("footer.copyright", { year }) }}</span>
    </p>
    <!-- Under a thin line, across the whole width: what the site is built
         with and the way to the details, then whether the backend answers -->
    <p class="technical">
      <span>
        {{ t("about.stack") }} ·
        <RouterLink :to="{ name: 'about' }">{{ t("about.footerLink") }}</RouterLink>
      </span>
      <ApiStatus />
    </p>
  </footer>
</template>

<style scoped>
/* One band across the whole width, in three columns: the sentence on the
   left, the links centred on the page, the privacy link and the copyright on
   the right. The two outer columns share the room left by the links, so the
   links stay centred whatever the length of the sentence. */
.footer {
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 8px 32px;
  padding: 12px 16px;
  border-top: 3px solid var(--mt-accent);
  background: var(--mt-blue-dark);
  color: #e3edf3;
  font-size: 0.85rem;
}

.footer a {
  color: #ffffff;
}

/* The sentence breaks where its text says so (the "\n" of the translation) */
.about {
  justify-self: start;
  margin: 0;
  white-space: pre-line;
  color: #b7cdd9;
}

/* The last line, across the three columns, under a thin line: the
   technologies on the left, the state of the API on the right */
.technical {
  grid-column: 1 / -1;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 4px 24px;
  margin: 2px 0 0;
  padding-top: 8px;
  border-top: 1px solid rgba(255, 255, 255, 0.15);
  font-size: 0.8rem;
}

/* The state of the API in lighter colours, readable on the dark blue */
.technical :deep(.online) {
  color: #86efac;
}

.technical :deep(.offline) {
  color: #fca5a5;
}

.technical :deep(.checking) {
  color: #b7cdd9;
}

/* The links on two rows of two, each one with the name of the profile
   after it */
.links {
  display: grid;
  grid-template-columns: auto auto;
  gap: 4px 24px;
  justify-self: center;
  margin: 0;
  padding: 0;
  list-style: none;
}

.links a {
  text-decoration: none;
  font-weight: 600;
}

.links a:hover {
  text-decoration: underline;
}

.who {
  margin-left: 4px;
  font-weight: normal;
  color: #b7cdd9;
}

/* The link above the copyright, both against the right edge */
.legal {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  justify-self: end;
  gap: 2px;
  margin: 0;
  white-space: nowrap;
  font-size: 0.78rem;
  color: #b7cdd9;
}

/* One column after the other on a narrow screen, everything on the left.
   Last, so that it wins over the rules above, which have the same weight */
@media (max-width: 900px) {
  .footer {
    grid-template-columns: 1fr;
  }

  .links,
  .legal {
    justify-self: start;
  }

  .legal {
    align-items: flex-start;
  }
}
</style>
