<!--
  frontend/src/pages/MyApplicationsPage.vue

  My applications page — the applications of the logged-in candidate
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/candidate/applications", to a candidate only
  (the router sends anyone else away). The applications as cards, newest
  first: the offer and its company, the date sent, the state as a pill and
  the states gone through, the files sent, a link to the offer, and the
  withdrawal while the employer has not decided, after a confirmation.
-->

<script setup lang="ts">
import { onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";

import { canWithdraw, listApplications, withdraw, type Application } from "../api/applications";
import { useApplicationText } from "../applications";
import { confirm } from "../confirm";

const { t } = useI18n();
const text = useApplicationText();

const applications = ref<Application[] | null>(null);
const loadFailed = ref(false);

// The application being withdrawn: its button is disabled meanwhile
const busy = ref<number | null>(null);
// The reason of a refused withdrawal, by application
const errors = ref<Record<number, string>>({});

async function load(): Promise<void> {
  loadFailed.value = false;
  try {
    applications.value = await listApplications();
  } catch {
    loadFailed.value = true;
  }
}

async function remove(application: Application): Promise<void> {
  const title = application.offer.title;
  if (!(await confirm(t("myApplications.confirmWithdraw", { title }), t("myApplications.withdraw")))) return;
  delete errors.value[application.id];
  busy.value = application.id;
  try {
    const answer = await withdraw(application.id);
    if (answer.status === 204) {
      applications.value = (applications.value ?? []).filter((item) => item.id !== application.id);
    } else {
      errors.value[application.id] = t("form.failed");
    }
  } catch {
    errors.value[application.id] = t("form.unreachable");
  } finally {
    busy.value = null;
  }
}

onMounted(load);
</script>

<template>
  <h1>{{ t("myApplications.title") }}</h1>

  <p v-if="loadFailed" class="error">{{ t("myApplications.loadFailed") }}</p>

  <template v-else-if="applications">
    <p v-if="applications.length === 0" class="muted">{{ t("myApplications.none") }}</p>
    <ul v-else class="cards">
      <li v-for="application in applications" :key="application.id" class="card">
        <p class="company">
          {{ application.offer.company.name }}
          <span class="pill" :class="application.status">{{ text.status(application.status) }}</span>
        </p>
        <h2 class="title">
          <RouterLink :to="{ name: 'offer', params: { id: application.offer.id } }">
            {{ application.offer.title }}
          </RouterLink>
        </h2>
        <p class="line">
          {{ application.offer.city }} · {{ t("applications.sentOn", { date: text.date(application.created_at) }) }}
          <span v-if="application.offer.status === 'closed'" class="muted"> · {{ t("myApplications.offerClosed") }}</span>
        </p>
        <p v-if="application.history.length > 1" class="history">{{ text.history(application) }}</p>
        <!-- The files sent, opened in a new tab -->
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
          <RouterLink :to="{ name: 'offer', params: { id: application.offer.id } }" class="secondary">
            {{ t("myApplications.offerLink") }}
          </RouterLink>
          <button
            v-if="canWithdraw(application)"
            type="button"
            class="as-link danger"
            :disabled="busy === application.id"
            @click="remove(application)"
          >
            {{ t("myApplications.withdraw") }}
          </button>
          <p v-if="errors[application.id]" class="error reason">{{ errors[application.id] }}</p>
        </div>
      </li>
    </ul>
  </template>
</template>

<style scoped>
.muted {
  color: var(--mt-muted);
}

.cards {
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

/* One application, a rule under each */
.card {
  padding: 20px 0;
  border-bottom: 1px solid var(--mt-border);
}

.company {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 0;
  color: var(--mt-muted);
  font-size: 0.9rem;
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

.title {
  margin: 2px 0 6px;
  font-size: 1.15rem;
}

.title a {
  text-decoration: none;
}

.title a:hover {
  text-decoration: underline;
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
  text-decoration: none;
}

.secondary:hover {
  background: var(--mt-border);
}

.danger {
  color: var(--mt-error);
}

.reason {
  flex-basis: 100%;
  margin: 0;
}
</style>
