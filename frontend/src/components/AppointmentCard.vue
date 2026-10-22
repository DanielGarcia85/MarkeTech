<!--
  frontend/src/components/AppointmentCard.vue

  Appointment card — one appointment, as the conversation and the calendar show it
  ───────────────────────────────────────────────────────────────────────────
  Used by ConversationPage, in the thread at the time it was proposed, and
  by AppointmentsPage, under the calendar for the one clicked. A small
  drawing of a calendar, the word "Appointment", its state as a pill and,
  when its last change is news, the mark "New" with a band of the accent;
  then when it takes place, where, what the employer adds, the answer of
  the candidate or the word of a cancellation, and the day it was
  proposed. Its buttons follow the side of the user: Accept and Decline
  for the candidate while it waits for an answer, Cancel for the employer
  until it takes place. The page does the moves (useAppointmentMoves) and
  passes back whether one is in flight and the reason of a refusal. In
  the calendar, the offer and the other participant, with the way to the
  conversation (about).
-->

<script setup lang="ts">
import { computed } from "vue";
import { useI18n } from "vue-i18n";

import type { Appointment } from "../api/appointments";
import { useAppointmentText } from "../appointments";
import Icon from "./Icon.vue";

const props = defineProps<{
  appointment: Appointment;
  // The side of the user: their buttons and the words of the answer
  role: "candidate" | "employer";
  // A move of this appointment in flight, and the reason of a refused one
  busy?: boolean;
  error?: string;
  // Under the calendar: the offer, the other participant, the way to the
  // conversation
  about?: boolean;
}>();

const emit = defineEmits<{ answer: [accept: boolean]; cancel: [] }>();

const { t, locale } = useI18n();
const text = useAppointmentText();

const canAnswer = computed(() => props.role === "candidate" && props.appointment.state === "pending");
const canCancel = computed(
  () =>
    props.role === "employer" &&
    (props.appointment.state === "pending" ||
      (props.appointment.state === "accepted" && new Date(props.appointment.starts_at) > new Date())),
);

// Whose words the response is, as the user reads them
const responseLabel = computed(() => {
  const answered = props.appointment.state === "accepted" || props.appointment.state === "declined";
  const key = answered ? "answer" : "cancellation";
  return t(`appointments.${key}.${props.role}`);
});

// "21 Oct, 18:10", the day it was proposed
function proposed(iso: string): string {
  return new Intl.DateTimeFormat(locale.value, {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}
</script>

<template>
  <article class="appointment" :class="[appointment.state, { unseen: appointment.new }]">
    <p class="top">
      <Icon name="calendar" />
      <strong>{{ t("appointments.title") }}</strong>
      <span class="pill" :class="appointment.state">{{ text.state(appointment.state) }}</span>
      <span v-if="appointment.new" class="news">{{ t("appointments.new") }}</span>
    </p>
    <p v-if="about" class="about">
      {{ appointment.about.other }} · {{ appointment.about.offer }}
    </p>
    <p class="when">{{ text.when(appointment) }}</p>
    <p class="place">{{ appointment.place }}</p>
    <p v-if="appointment.note" class="note">{{ appointment.note }}</p>
    <blockquote v-if="appointment.response" class="response">
      <span class="label">{{ responseLabel }}</span><span>{{ appointment.response }}</span>
    </blockquote>
    <p class="meta">{{ t("appointments.proposed", { date: proposed(appointment.created_at) }) }}</p>
    <p v-if="canAnswer || canCancel || about" class="actions">
      <template v-if="canAnswer">
        <button type="button" class="primary" :disabled="busy" @click="emit('answer', true)">
          {{ t("appointments.accept") }}
        </button>
        <button type="button" class="secondary" :disabled="busy" @click="emit('answer', false)">
          {{ t("appointments.decline") }}
        </button>
      </template>
      <button v-if="canCancel" type="button" class="secondary" :disabled="busy" @click="emit('cancel')">
        {{ t("appointments.cancel") }}
      </button>
      <RouterLink v-if="about" :to="{ name: 'conversation', params: { id: appointment.application } }">
        {{ t("appointments.openConversation") }}
      </RouterLink>
    </p>
    <p v-if="error" class="error">{{ error }}</p>
  </article>
</template>

<style scoped>
/* A box of its own among the bubbles, the whole width of the thread */
.appointment {
  padding: 14px 18px;
  border: 1px solid var(--mt-border);
  border-left: 4px solid var(--mt-blue);
  border-radius: 10px;
  background: var(--mt-surface);
}

/* The band on the left says the state at a glance */
.appointment.pending {
  border-left-color: var(--mt-accent);
}

.appointment.accepted {
  border-left-color: var(--mt-success);
}

.appointment.declined {
  border-left-color: var(--mt-error);
}

.appointment.cancelled,
.appointment.expired {
  border-left-color: var(--mt-muted);
}

/* News: the whole box in the light accent */
.appointment.unseen {
  background: var(--mt-accent-surface);
}

.top {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 6px 10px;
  margin: 0 0 8px;
}

.top .icon {
  color: var(--mt-blue);
}

.about {
  margin: 0 0 4px;
  color: var(--mt-muted);
}

.when {
  margin: 0;
  font-weight: 600;
}

/* What was said: the line breaks kept */
.place,
.note {
  margin: 2px 0 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.note {
  color: var(--mt-muted);
}

/* The answer or the word of a cancellation, as a quotation */
.response {
  margin: 10px 0 0;
  padding: 8px 12px;
  border-left: 3px solid var(--mt-border);
  background: var(--mt-background);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.label {
  display: block;
  color: var(--mt-muted);
  font-size: 0.85rem;
}

.meta {
  margin: 8px 0 0;
  color: var(--mt-muted);
  font-size: 0.8rem;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 8px 16px;
  margin: 12px 0 0;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 6px;
  background: var(--mt-background);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}

.secondary:hover {
  background: var(--mt-border);
}

.secondary:disabled {
  opacity: 0.6;
  cursor: default;
}

/* The state: amber while waiting, green accepted, red declined, grey
   cancelled or expired */
.pill {
  display: inline-block;
  padding: 1px 10px;
  border: 1px solid var(--mt-border);
  border-radius: 999px;
  background: var(--mt-background);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.pill.pending {
  border-color: var(--mt-accent);
  color: var(--mt-accent-dark);
}

.pill.accepted {
  border-color: var(--mt-success-surface);
  background: var(--mt-success-surface);
  color: var(--mt-success);
}

.pill.declined {
  border-color: var(--mt-error);
  color: var(--mt-error);
}

.pill.cancelled,
.pill.expired {
  color: var(--mt-muted);
}

/* "New", in the accent, as on the cards of the applications */
.news {
  padding: 1px 10px;
  border-radius: 999px;
  background: var(--mt-background);
  color: var(--mt-accent-dark);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
</style>
