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
  window, the bar becomes a strip under the header, where each group keeps
  its title and its links on one line, and wraps as a whole.
-->

<script setup lang="ts">
import { watch } from "vue";
import { useI18n } from "vue-i18n";

import { followNotifications, useNotifications } from "../notifications";
import { useSession } from "../session";
import Icon from "./Icon.vue";

const { t } = useI18n();
const session = useSession();
const counts = useNotifications();

// The counts follow whoever is logged in: read every minute, or emptied
watch(() => session.user?.id, (id) => followNotifications(id !== undefined), { immediate: true });
</script>

<template>
  <nav class="sidebar" :aria-label="t('nav.label')">
    <div class="inner">
      <div class="block">
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
      <div v-if="session.user?.role" class="block">
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
      <div v-if="session.user" class="block">
        <p class="group">{{ t("nav.account") }}</p>
        <RouterLink :to="{ name: 'profile' }"><Icon name="user" />{{ t("nav.profile") }}</RouterLink>
        <RouterLink :to="{ name: 'credentials' }"><Icon name="key" />{{ t("nav.credentials") }}</RouterLink>
      </div>
      <div class="block">
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
@media (max-width: 900px) {
  .sidebar {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 24px;
    width: auto;
    padding: 8px 16px;
    border-right: none;
    border-bottom: 1px solid var(--mt-border);
  }

  /* The strip scrolls away with the page */
  .inner {
    position: static;
    display: contents;
    max-height: none;
    overflow: visible;
  }

  .block {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 4px 8px;
  }

  .block + .block {
    margin-top: 0;
  }

  .group {
    margin: 0 4px 0 0;
  }

  .sidebar a {
    padding: 6px 10px;
  }
}
</style>
