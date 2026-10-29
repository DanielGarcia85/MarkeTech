<!--
  frontend/src/components/AppFooter.vue

  Footer — what the site is built with, where to find more, how to get in touch
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue under the current page, and kept at the bottom of the
  window while the page scrolls, on every width (decision of 29.10.2026).
  One band across the whole width, in the dark blue with light text, under
  a thin line in the accent colour: on the left, in one paragraph, the
  technologies of the site, the way to the about page and whether the
  backend answers (ApiStatus); the links on two rows in the centre; the terms and privacy
  links above the copyright on the right.
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
    <!-- What the site is built with, the way to the details and whether
         the backend answers, one after the other -->
    <p class="technical">
      {{ t("about.stack") }}&nbsp;·
      <RouterLink :to="{ name: 'about' }" class="whole">{{ t("about.footerLink") }}</RouterLink>&nbsp;·
      <span class="whole"><ApiStatus /></span>
    </p>
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
  </footer>
</template>

<style scoped>
/* One band across the whole width, in three columns: the technologies on
   the left, the links centred on the page, the legal links and the
   copyright on the right. The two outer columns share the room left by the
   links, so the links stay centred whatever the length of the technologies.
   Sticky at the bottom: it stays in the flow of the page, so nothing is
   hidden under it, and it is drawn above the page that scrolls behind.
   Small type and tight lines, so that it stays thin: two lines on a wide
   window (decision of 29.10.2026) */
.footer {
  position: sticky;
  bottom: 0;
  z-index: 10;
  display: grid;
  grid-template-columns: 1fr auto 1fr;
  align-items: center;
  gap: 8px 32px;
  padding: 6px 16px;
  border-top: 3px solid var(--mt-accent);
  background: var(--mt-blue-dark);
  color: #e3edf3;
  font-size: 0.8rem;
  line-height: 1.35;
}

.footer a {
  color: #ffffff;
}

/* The technologies, the about link and the state of the API in one
   paragraph against the left edge, on two lines when the window is wide
   enough, never reaching the links in the centre */
.technical {
  justify-self: start;
  max-width: 560px;
  margin: 0;
  font-size: 0.75rem;
  color: #b7cdd9;
}

/* The about link and the state of the API are never cut in two */
.whole {
  white-space: nowrap;
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
  gap: 0 24px;
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
  font-size: 0.75rem;
  color: #b7cdd9;
}

/* One column after the other on a narrow screen, everything on the left.
   Last, so that it wins over the rules above, which have the same weight */
@media (max-width: 900px) {
  .footer {
    grid-template-columns: 1fr;
    gap: 6px;
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
