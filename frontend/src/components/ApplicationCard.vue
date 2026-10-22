<!--
  frontend/src/components/ApplicationCard.vue

  Application card — one application, as its employer sees it
  ───────────────────────────────────────────────────────────────────────────
  Used by the page of the applications received, grouped by offer. A mark
  "New" and a band of the accent on the left when it arrived since the
  employer last looked (unseen). The candidate and their
  contact details, the date, the state as a pill and the states gone
  through, the files as links, the way to the conversation with the
  candidate (while the application is in progress, or once a conversation
  exists, with its unread messages), and the moves of the state as buttons
  (all but the current state), which the page carries out: the card only
  says which one was asked.
-->

<script setup lang="ts">
import { useI18n } from "vue-i18n";

import { EMPLOYER_STATUSES, type Application, type ApplicationStatus } from "../api/applications";
import { useApplicationText } from "../applications";

defineProps<{
  application: Application;
  // A move is in flight: the buttons are disabled meanwhile
  busy?: boolean;
  // The reason of a refused move, shown under the buttons
  error?: string;
  // The unread messages of its conversation; undefined when it has none
  unread?: number;
}>();

defineEmits<{ move: [status: ApplicationStatus] }>();

const { t } = useI18n();
const text = useApplicationText();
</script>

<template>
  <article class="card" :class="{ unseen: application.unseen }">
    <p class="head">
      <strong class="name">{{ text.name(application) }}</strong>
      <span class="pill" :class="application.status">{{ text.status(application.status) }}</span>
      <span v-if="application.unseen" class="news">{{ t("applications.new") }}</span>
    </p>
    <!-- The contact details, read on the profile of the candidate -->
    <p class="line">
      <a :href="'mailto:' + application.candidate.email">{{ application.candidate.email }}</a>
      <template v-if="application.candidate.phone"> · {{ application.candidate.phone }}</template>
      <template v-if="application.candidate.city"> · {{ application.candidate.city }}</template>
    </p>
    <p class="line">{{ t("applications.sentOn", { date: text.date(application.created_at) }) }}</p>
    <p v-if="application.history.length > 1" class="history">{{ text.history(application) }}</p>
    <p class="files">
      <a :href="application.cv.url" target="_blank" rel="noopener">{{ t("applications.cv") }}</a>
      <a v-if="application.cover_letter" :href="application.cover_letter.url" target="_blank" rel="noopener">
        {{ t("applications.coverLetter") }}
      </a>
      <a
        v-for="attachment in application.attachments"
        :key="attachment.id"
        :href="attachment.url"
        target="_blank"
        rel="noopener"
      >
        {{ attachment.name }}
      </a>
    </p>
    <div class="actions">
      <RouterLink
        v-if="application.status === 'in_progress' || unread !== undefined"
        :to="{ name: 'conversation', params: { id: application.id } }"
        class="secondary messages"
      >
        {{ t("messaging.button") }}
        <span v-if="unread" class="count">{{ unread }}</span>
      </RouterLink>
      <button
        v-for="status in EMPLOYER_STATUSES.filter((s) => s !== application.status)"
        :key="status"
        type="button"
        :class="status === 'accepted' ? 'primary' : 'secondary'"
        :disabled="busy"
        @click="$emit('move', status)"
      >
        {{ t("receivedApplications.set." + status) }}
      </button>
      <p v-if="error" class="error reason">{{ error }}</p>
    </div>
  </article>
</template>

<style scoped>
/* One application in a box, as the offers are shown */
.card {
  margin-bottom: 12px;
  padding: 18px 20px;
  border: 1px solid var(--mt-border);
  border-radius: 12px;
  background: var(--mt-background);
}

/* Arrived since the last visit: a band of the accent on the left */
.card.unseen {
  border-left: 4px solid var(--mt-accent);
}

/* "New", in the accent */
.news {
  padding: 1px 10px;
  border-radius: 999px;
  background: var(--mt-accent-surface);
  color: var(--mt-accent-dark);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.head {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0 0 4px;
}

.name {
  font-size: 1.1rem;
}

/* The state of the application: grey when received, blue in progress,
   green once accepted, red when rejected */
.pill {
  display: inline-block;
  padding: 1px 10px;
  border: 1px solid var(--mt-border);
  border-radius: 999px;
  background: var(--mt-surface);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.pill.in_progress {
  border-color: var(--mt-blue);
  color: var(--mt-blue);
}

.pill.accepted {
  border-color: var(--mt-success-surface);
  background: var(--mt-success-surface);
  color: var(--mt-success);
}

.pill.rejected {
  border-color: var(--mt-error);
  color: var(--mt-error);
}

.line {
  margin: 0 0 2px;
}

.history {
  margin: 0 0 6px;
  color: var(--mt-muted);
  font-size: 0.85rem;
}

/* The files side by side */
.files {
  display: flex;
  flex-wrap: wrap;
  gap: 4px 16px;
  margin: 0;
}

/* The buttons, side by side, under the text of the card */
.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  margin-top: 12px;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}

.secondary:hover {
  background: var(--mt-border);
}

/* The way to the conversation, a link styled as the buttons beside it */
.messages {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  text-decoration: none;
}

.count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 999px;
  background: var(--mt-accent);
  color: #ffffff;
  font-size: 0.75rem;
  font-weight: 600;
}

.secondary:disabled {
  opacity: 0.6;
  cursor: default;
}

/* The reason of a refused move takes a whole line under the buttons */
.reason {
  flex-basis: 100%;
  margin: 0;
}
</style>
