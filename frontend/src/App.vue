<!--
  frontend/src/App.vue

  Root component — top of the component tree, and the page shell
  ───────────────────────────────────────────────────────────────────────────
  Mounted by main.ts. Asks the backend who is logged in, then lays out the
  three bands of every page: the header, the body (the side bar, the
  current page, then the reviews on a wide window) and the footer, plus the
  confirmation dialog that any page may open. The body stretches so that
  the footer sits at the bottom of the window, even on a short page, and
  the footer stays there while the page scrolls. A demo account sees a
  band under the header (shared, made again every night), kept at the top
  of the window with it; the two side bars stay in view between the top
  and the footer while the page scrolls (their heights in --mt-top and
  --mt-bottom).
  Every page is declared in router.ts.
-->

<script setup lang="ts">
import { onBeforeUnmount, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import AppFooter from "./components/AppFooter.vue";
import AppHeader from "./components/AppHeader.vue";
import AppSidebar from "./components/AppSidebar.vue";
import ConfirmDialog from "./components/ConfirmDialog.vue";
import ReviewsAside from "./components/ReviewsAside.vue";
import { loadSession, useSession } from "./session";

const { t } = useI18n();
const session = useSession();
const route = useRoute();

// Runs once, when the application starts
loadSession();

// The height of the header and of the band, kept in --mt-top for the two
// side bars, which stay in view under them while the page scrolls. Read
// again whenever it changes: the band comes and goes with a demo account,
// the header wraps on a narrow window
const top = ref<HTMLElement | null>(null);
const observer = new ResizeObserver(([entry]) => {
  const height = entry.target.getBoundingClientRect().height;
  document.documentElement.style.setProperty("--mt-top", `${height}px`);
});
onMounted(() => top.value && observer.observe(top.value));

// The height of the footer, kept in --mt-bottom for the same side bars,
// which must stop above it. It changes with the language and with the
// width of the window, where its columns wrap or pile up. The ref of a
// component gives the component: its root element is in $el
const bottom = ref<{ $el: HTMLElement } | null>(null);
const footerObserver = new ResizeObserver(([entry]) => {
  const height = entry.target.getBoundingClientRect().height;
  document.documentElement.style.setProperty("--mt-bottom", `${height}px`);
});
onMounted(() => bottom.value && footerObserver.observe(bottom.value.$el));

onBeforeUnmount(() => {
  observer.disconnect();
  footerObserver.disconnect();
});
</script>

<template>
  <div class="shell">
    <!-- The header and the band of a demo account stay at the top of the
         window together while the page scrolls -->
    <div ref="top" class="top">
      <AppHeader />
      <p v-if="session.user?.is_demo" class="demo-band">{{ t("demo.band") }}</p>
    </div>
    <div class="body">
      <!-- The navigation, before the page: the offers for everyone, more
           for a logged-in user -->
      <AppSidebar />
      <main class="page">
        <RouterView />
      </main>
      <!-- The reviews of the platform, on a wide window, on every page but
           their own list -->
      <ReviewsAside v-if="route.name !== 'reviews'" />
    </div>
    <AppFooter ref="bottom" />
    <!-- Invisible until a page asks a question -->
    <ConfirmDialog />
  </div>
</template>

<style scoped>
/* The header and the band, fixed together at the top of the window while
   the page scrolls under them: drawn above the page */
.top {
  position: sticky;
  top: 0;
  z-index: 10;
}

/* A demo account: a thin band of the accent under the header, in small
   type so that it stays thin */
.demo-band {
  margin: 0;
  padding: 2px 16px;
  border-bottom: 1px solid var(--mt-accent);
  background: var(--mt-accent-surface);
  color: var(--mt-accent-dark);
  font-size: 0.8rem;
  font-weight: 500;
  text-align: center;
}

/* The whole window, as a column: header, body, footer */
.shell {
  display: flex;
  flex-direction: column;
  min-height: 100dvh;
}

/* The body takes all the height left by the header and the footer */
.body {
  display: flex;
  flex: 1;
}

/* The page takes all the width left by the side bar */
.page {
  flex: 1;
  min-width: 0;
}

/* Narrow window: the side bar becomes a strip above the page */
@media (max-width: 900px) {
  .body {
    flex-direction: column;
  }
}
</style>
