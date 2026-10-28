<!--
  frontend/src/components/AppSidebar.vue

  Side bar — the navigation, on every page
  ───────────────────────────────────────────────────────────────────────────
  Displayed by App.vue on the left of the page, for everyone: a visitor
  gets the list of the offers only, so that the pages keep the same layout
  before and after logging in; a logged-in user gets the links of their
  role (with the number of applications that bring news: arrived for an
  employer, moved for a candidate), their conversations (open and closed,
  each with the number of unread messages) and their appointments (with
  the number that bring news), and their account (the
  profile, then the e-mail address and the password); last, for everyone,
  the platform: all the reviews, and one's own for a candidate or an
  employer (decisions of 23.10.2026); each link with a
  small drawing before it (Icon). The counts are kept fresh by
  notifications.ts. One group
  of links per area of the application; a group gets its links when the
  pages exist, never before. On a narrow
  window, the bar becomes a strip under the header that shows only the
  titles of the groups, as buttons with the sum of their counts; a click
  opens the links of that group under them (one group at a time), and
  going to another page closes it (decision of 26.10.2026).
-->

<script setup lang="ts">
import { computed, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { followLive } from "../live";
import { followNotifications, useNotifications } from "../notifications";
import { useSession } from "../session";
import Icon from "./Icon.vue";

const { t } = useI18n();
const session = useSession();
const counts = useNotifications();

// The counts and the WebSocket follow whoever is logged in: read and
// opened for a user, emptied and closed for nobody
watch(
  () => session.user?.id,
  (id) => {
    followNotifications(id !== undefined);
    followLive(id);
  },
  { immediate: true },
);

// ── The narrow window ─────────────────────────────────────────────────
// Only the titles of the groups show, as buttons; one group is open at a
// time, none at first

type Group = "offers" | "messaging" | "account" | "platform";

const route = useRoute();
const open = ref<Group | null>(null);

function toggle(group: Group): void {
  open.value = open.value === group ? null : group;
}

// Another page: the strip closes, the page gets the room
watch(() => route.fullPath, () => (open.value = null));

// The groups the user has, in the order of the bar
const groups = computed<Group[]>(() => [
  "offers",
  ...(session.user?.role ? (["messaging"] as const) : []),
  ...(session.user ? (["account"] as const) : []),
  "platform",
]);

// The news of a group, on its button: the sum of the counts of its links
const news = computed<Record<Group, number>>(() => ({
  offers: counts.applications,
  messaging: counts.open + counts.closed + counts.appointments,
  account: 0,
  platform: 0,
}));

// The group of the page shown, marked on its button
const PAGES: Record<Group, string[]> = {
  offers: ["home", "offer", "apply", "myOffers", "offerNew", "offerEdit", "receivedApplications", "myApplications", "myFavorites"],
  messaging: ["conversations", "closedConversations", "conversation", "appointments"],
  account: ["profile", "credentials"],
  platform: ["reviews", "myReview"],
};
const current = computed(() => groups.value.find((group) => PAGES[group].includes(String(route.name))));
</script>

<template>
  <nav class="sidebar" :aria-label="t('nav.label')">
    <!-- Narrow window only: the titles of the groups, as buttons -->
    <div class="tabs">
      <button
        v-for="group in groups"
        :key="group"
        type="button"
        class="tab"
        :class="{ current: current === group }"
        :aria-expanded="open === group"
        @click="toggle(group)"
      >
        {{ t(`nav.${group}`) }}
        <span v-if="news[group]" class="count">{{ news[group] }}</span>
        <span class="chevron" aria-hidden="true">{{ open === group ? "▴" : "▾" }}</span>
      </button>
    </div>
    <div class="inner">
      <div class="block" :class="{ open: open === 'offers' }">
        <p class="group">{{ t("nav.offers") }}</p>
        <RouterLink :to="{ name: 'home' }"><Icon name="briefcase" />{{ t("nav.allOffers") }}</RouterLink>
        <RouterLink v-if="session.user?.role === 'employer'" :to="{ name: 'myOffers' }">
          <Icon name="clipboard" />{{ t("nav.myOffers") }}
        </RouterLink>
        <RouterLink v-if="session.user?.role === 'employer'" :to="{ name: 'receivedApplications' }">
          <Icon name="inbox" />{{ t("nav.receivedApplications") }}
          <span v-if="counts.applications" class="count">{{ counts.applications }}</span>
        </RouterLink>
        <RouterLink v-if="session.user?.role === 'candidate'" :to="{ name: 'myApplications' }">
          <Icon name="send" />{{ t("nav.myApplications") }}
          <span v-if="counts.applications" class="count">{{ counts.applications }}</span>
        </RouterLink>
        <RouterLink v-if="session.user?.role === 'candidate'" :to="{ name: 'myFavorites' }">
          <Icon name="heart" />{{ t("nav.myFavorites") }}
        </RouterLink>
      </div>
      <div v-if="session.user?.role" class="block" :class="{ open: open === 'messaging' }">
        <p class="group">{{ t("nav.messaging") }}</p>
        <RouterLink :to="{ name: 'conversations' }">
          <Icon name="chat" />{{ t("nav.openConversations") }}
          <span v-if="counts.open" class="count">{{ counts.open }}</span>
        </RouterLink>
        <RouterLink :to="{ name: 'closedConversations' }">
          <Icon name="archive" />{{ t("nav.closedConversations") }}
          <span v-if="counts.closed" class="count">{{ counts.closed }}</span>
        </RouterLink>
        <RouterLink :to="{ name: 'appointments' }">
          <Icon name="calendar" />{{ t("nav.appointments") }}
          <span v-if="counts.appointments" class="count">{{ counts.appointments }}</span>
        </RouterLink>
      </div>
      <div v-if="session.user" class="block" :class="{ open: open === 'account' }">
        <p class="group">{{ t("nav.account") }}</p>
        <RouterLink :to="{ name: 'profile' }"><Icon name="user" />{{ t("nav.profile") }}</RouterLink>
        <RouterLink :to="{ name: 'credentials' }"><Icon name="key" />{{ t("nav.credentials") }}</RouterLink>
      </div>
      <div class="block" :class="{ open: open === 'platform' }">
        <p class="group">{{ t("nav.platform") }}</p>
        <RouterLink :to="{ name: 'reviews' }"><Icon name="star" />{{ t("nav.allReviews") }}</RouterLink>
        <RouterLink v-if="session.user?.role" :to="{ name: 'myReview' }">
          <Icon name="pencil" />{{ t("nav.myReview") }}
        </RouterLink>
      </div>
    </div>
  </nav>
</template>

<style scoped>
/* Wide enough for the longest link, its drawing before it and its count
   after it, on one line: "Candidatures reçues" with its count needs a
   link of 247 px, its count then lined up with the others (measured on
   22.10.2026) */
.sidebar {
  flex: none;
  width: 272px;
  padding: 20px 12px;
  border-right: 1px solid var(--mt-border);
  background: var(--mt-surface);
}

/* The links stay in view while the page scrolls, under the header (its
   height in --mt-top, set by App.vue); the column keeps its colour down to
   the footer. A window too short for all the links scrolls them */
.inner {
  position: sticky;
  top: calc(var(--mt-top, 64px) + 20px);
  max-height: calc(100dvh - var(--mt-top, 64px) - 40px);
  overflow-y: auto;
}

/* The buttons of the groups: only on a narrow window */
.tabs {
  display: none;
}

/* The title of a group of links: small capitals, muted */
.group {
  margin: 0 10px 6px;
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: var(--mt-muted);
}

/* A gap above every group but the first */
.block + .block {
  margin-top: 20px;
}

/* One link per line, its drawing before its words, in the muted colour
   until the link is the current page or under the pointer; the page
   being shown is marked by the router with the class router-link-active */
.sidebar a {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 6px;
  color: var(--mt-text);
  text-decoration: none;
  white-space: nowrap;
}

.sidebar a .icon {
  color: var(--mt-muted);
}

.sidebar a:hover .icon,
.sidebar a.router-link-active .icon {
  color: inherit;
}

/* The unread messages, a small round of the accent at the end of the link */
.count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  margin-left: auto;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--mt-accent);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 600;
}

.sidebar a:hover {
  background: var(--mt-border);
}

.sidebar a.router-link-active {
  background: var(--mt-blue);
  color: #ffffff;
}

/* Narrow window: a strip under the header; each group is a line of its
   own title and links, the groups side by side while the width allows,
   then one under the other, aligned on the left */
/* Narrow window: a strip under the header with the titles of the groups
   as buttons; the links of the open group under them, on one line that
   wraps. Last, so that it wins over the rules above (section 10 of
   CLAUDE.md) */
@media (max-width: 900px) {
  .sidebar {
    width: auto;
    padding: 8px 16px;
    border-right: none;
    border-bottom: 1px solid var(--mt-border);
  }

  .tabs {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }

  /* A title as a button: small capitals, the count after it, a chevron */
  .tab {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 10px;
    border: 1px solid var(--mt-border);
    border-radius: 6px;
    background: var(--mt-background);
    color: var(--mt-muted);
    font: inherit;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    cursor: pointer;
  }

  .tab .count {
    margin-left: 0;
  }

  /* The group of the page shown: in the brand colour */
  .tab.current {
    border-color: var(--mt-blue);
    color: var(--mt-blue);
  }

  .tab[aria-expanded="true"] {
    background: var(--mt-blue);
    border-color: var(--mt-blue);
    color: #ffffff;
  }

  .chevron {
    font-size: 0.7rem;
  }

  /* The strip scrolls away with the page */
  .inner {
    position: static;
    max-height: none;
    overflow: visible;
  }

  /* Only the open group, its links on one line that wraps; its title is
     on its button already */
  .block {
    display: none;
  }

  .block.open {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 8px;
    margin-top: 8px;
  }

  .group {
    display: none;
  }

  .sidebar a {
    padding: 6px 10px;
  }
}
</style>
