<!--
  frontend/src/pages/AppointmentsPage.vue

  Appointments page — the appointments of the user, in a calendar
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/appointments", to a logged-in user of either role. A
  calendar (vue-cal, decision of 22.10.2026) by month, week or day, Monday
  to Friday (no appointment is proposed on a weekend: decisions of
  23.10.2026), in the language displayed, each appointment in the colour of its state: amber
  while it waits for an answer, green accepted, red declined, grey
  cancelled or expired. A click on one shows its card under the calendar,
  with the offer, the other participant, the way to the conversation, and
  the buttons of the user's side (answer, cancel); the page scrolls just
  enough for the whole card to be seen. Next to it, the
  appointments to come. The calendar asks the API for the period it shows,
  again at every change of view; reading marks the news seen, after which
  the counts of the side bar are read again (notifications.ts).
-->

<script setup lang="ts">
import { computed, nextTick, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import VueCal from "vue-cal";
import "vue-cal/dist/vuecal.css";

import { myAppointments, type Appointment } from "../api/appointments";
import { useAppointmentMoves, useAppointmentText } from "../appointments";
import AppointmentCard from "../components/AppointmentCard.vue";
import EmptyState from "../components/EmptyState.vue";
import { refreshNotifications } from "../notifications";
import { useSession } from "../session";

const { t, locale } = useI18n();
const session = useSession();
const text = useAppointmentText();

const role = computed(() => (session.user?.role === "candidate" ? "candidate" : "employer"));

// The appointments of the period shown, and those to come
const shown = ref<Appointment[]>([]);
const coming = ref<Appointment[]>([]);
const failed = ref(false);
// The appointment clicked, shown under the calendar
const selectedId = ref<number | null>(null);
// The ids that were news when the page opened: they keep their mark for
// the visit, though the API has marked them seen
const news = new Set<number>();

const selected = computed(
  () =>
    shown.value.find((item) => item.id === selectedId.value) ??
    coming.value.find((item) => item.id === selectedId.value) ??
    null,
);

// The events of vue-cal: their time, two lines of text, the class of
// their state (the colours below). The first line is what tells the
// appointments apart: the offer for a candidate (the company is often the
// same), the candidate for an employer
const events = computed(() =>
  shown.value.map((appointment) => ({
    id: appointment.id,
    start: new Date(appointment.starts_at),
    end: new Date(appointment.ends_at),
    title: role.value === "candidate" ? appointment.about.offer : appointment.about.other,
    content: role.value === "candidate" ? appointment.about.other : appointment.about.offer,
    class: appointment.state + (news.has(appointment.id) ? " new" : ""),
  })),
);

// Remembers the news of a reading, and keeps the mark on them
function marked(list: Appointment[]): Appointment[] {
  for (const item of list) if (item.new) news.add(item.id);
  return list.map((item) => (news.has(item.id) ? { ...item, new: true } : item));
}

// The period vue-cal shows: from its first cell to the end of its last one
type Period = { startDate: Date; endDate: Date; firstCellDate?: Date; lastCellDate?: Date };

async function loadPeriod(period: Period): Promise<void> {
  const start = period.firstCellDate ?? period.startDate;
  const last = period.lastCellDate ?? period.endDate;
  const end = new Date(last.getFullYear(), last.getMonth(), last.getDate() + 1);
  try {
    shown.value = marked(await myAppointments(start.toISOString(), end.toISOString()));
    failed.value = false;
    refreshNotifications();
  } catch {
    failed.value = true;
  }
}

async function loadComing(): Promise<void> {
  try {
    const now = new Date();
    coming.value = marked(await myAppointments(now.toISOString())).filter(
      (item) => item.state === "pending" || item.state === "accepted",
    );
    refreshNotifications();
  } catch {
    failed.value = true;
  }
}

// The card of the appointment chosen, under the calendar
const card = ref<{ $el: HTMLElement } | null>(null);

// Shows an appointment under the calendar, and scrolls down to it when
// the window does not show it whole
async function show(id: number): Promise<void> {
  selectedId.value = id;
  await nextTick();
  card.value?.$el.scrollIntoView({ behavior: "smooth", block: "nearest" });
}

// A click on an event of the calendar
function select(event: { id: number }): void {
  show(event.id);
}

// An answer or a cancellation: the appointment takes its new state in both lists
const moves = useAppointmentMoves((moved) => {
  const replace = (list: Appointment[]) => list.map((item) => (item.id === moved.id ? moved : item));
  shown.value = replace(shown.value);
  coming.value = replace(coming.value).filter((item) => item.state === "pending" || item.state === "accepted");
  refreshNotifications();
});

// "Thu 26 Oct, 10:00", the line of an appointment to come
function short(appointment: Appointment): string {
  return new Intl.DateTimeFormat(locale.value, {
    weekday: "short",
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(appointment.starts_at));
}

onMounted(loadComing);
</script>

<template>
  <h1>{{ t("appointments.pageTitle") }}</h1>
  <p class="intro">{{ t(`appointments.intro.${role}`) }}</p>
  <p v-if="failed" class="error">{{ t("appointments.loadFailed") }}</p>

  <div class="layout">
    <div class="calendar">
      <VueCal
        :locale="locale"
        active-view="month"
        :disable-views="['years', 'year']"
        :time-from="7 * 60"
        :time-to="20 * 60"
        :time-step="60"
        events-on-month-view="short"
        hide-weekends
        :events="events"
        :on-event-click="select"
        today-button
        @ready="loadPeriod"
        @view-change="loadPeriod"
      />
    </div>

    <aside class="coming">
      <h2>{{ t("appointments.coming") }}</h2>
      <EmptyState v-if="coming.length === 0" icon="calendar" :text="t('appointments.noneComing')" />
      <ul v-else>
        <li v-for="appointment in coming" :key="appointment.id">
          <button type="button" class="line" :class="appointment.state" @click="show(appointment.id)">
            <span class="dot" aria-hidden="true"></span>
            <span>
              <strong>{{ short(appointment) }}</strong>
              <span class="who">{{ appointment.about.other }} · {{ appointment.about.offer }}</span>
              <span class="state">{{ text.state(appointment.state) }}</span>
            </span>
          </button>
        </li>
      </ul>
    </aside>
  </div>

  <AppointmentCard
    v-if="selected"
    ref="card"
    class="selected"
    :appointment="selected"
    :role="role"
    :busy="moves.busy.value === selected.id"
    :error="moves.errors.value[selected.id]"
    about
    @answer="(accept) => moves.answer(selected!, accept)"
    @cancel="moves.cancel(selected!)"
  />
  <p v-else class="muted hint">{{ t("appointments.clickHint") }}</p>
</template>

<style scoped>
.intro {
  margin: 0 0 16px;
  color: var(--mt-muted);
}

/* The calendar, and the appointments to come on its right */
.layout {
  display: grid;
  grid-template-columns: minmax(0, 1fr) 280px;
  gap: 24px;
  align-items: start;
}

.calendar {
  height: 440px;
  border: 1px solid var(--mt-border);
  border-radius: 10px;
  overflow: hidden;
}

.coming h2 {
  margin: 0 0 12px;
  color: var(--mt-blue);
  font-size: 1.1rem;
}

.coming ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

/* One appointment to come: a dot of its state, the day, who and what */
.line {
  display: flex;
  gap: 10px;
  width: 100%;
  margin-bottom: 8px;
  padding: 10px 12px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-background);
  color: var(--mt-text);
  font: inherit;
  text-align: left;
  cursor: pointer;
}

.line:hover {
  border-color: var(--mt-blue-border);
  background: var(--mt-blue-surface);
}

.line > span:last-child {
  display: flex;
  flex-direction: column;
}

.dot {
  flex: none;
  width: 10px;
  height: 10px;
  margin-top: 6px;
  border-radius: 50%;
  background: var(--mt-success);
}

.line.pending .dot {
  background: var(--mt-accent);
}

.who,
.state {
  color: var(--mt-muted);
  font-size: 0.85rem;
}

.selected {
  margin-top: 24px;
}

.hint {
  margin-top: 16px;
  color: var(--mt-muted);
}

/* Narrow window: the appointments to come under the calendar */
@media (max-width: 1100px) {
  .layout {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>

<style>
/* The calendar in the colours of the site (vue-cal's own classes, hence
   not scoped). The bar of the title and the views in the light blue */
.vuecal__menu,
.vuecal__title-bar {
  background: var(--mt-blue-surface);
}

.vuecal__view-btn--active {
  border-bottom-color: var(--mt-blue);
  color: var(--mt-blue);
}

.vuecal__cell--today,
.vuecal__cell--current {
  background: rgba(45, 111, 145, 0.05);
}

.vuecal__cell--selected {
  background: rgba(45, 111, 145, 0.1);
}

/* An appointment: a band of its state on the left, its text in the colour
   of the text */
.vuecal__event {
  border-left: 3px solid var(--mt-success);
  background: var(--mt-success-surface);
  color: var(--mt-text);
  font-size: 0.8rem;
  text-align: left;
  cursor: pointer;
}

.vuecal__event.pending {
  border-left-color: var(--mt-accent);
  background: var(--mt-accent-surface);
}

.vuecal__event.declined {
  border-left-color: var(--mt-error);
  background: #fde8e8;
}

.vuecal__event.cancelled,
.vuecal__event.expired {
  border-left-color: var(--mt-muted);
  background: var(--mt-surface);
  color: var(--mt-muted);
  text-decoration: line-through;
}

.vuecal__event.new {
  box-shadow: inset 0 0 0 2px var(--mt-accent);
}

.vuecal__event-title {
  font-weight: 600;
}

/* vue-cal writes "No event" in the empty days of a week: the empty grid
   says it already */
.vuecal__no-event {
  display: none;
}
</style>
