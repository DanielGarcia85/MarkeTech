// frontend/src/appointments.ts
//
// Appointment texts and moves — what the conversation and the calendar share
// ─────────────────────────────────────────────────────────────────────────────
// The lines both pages write about an appointment: when it takes place, as
// one line, and its state. And the moves on it, each after a confirmation:
// the answer of the candidate, a message required (decisions of
// 22.10.2026), and the cancellation by the employer, a word optional. The
// answer of the API comes back to the page through "moved", which puts it
// in place of the old one. Composables, because the words and the date
// formats depend on the language displayed.

import { ref } from "vue";
import { useI18n } from "vue-i18n";

import {
  answerAppointment,
  cancelAppointment,
  type Appointment,
  type AppointmentState,
} from "./api/appointments";
import { firstErrorOf } from "./api/offers";
import { confirmWithText } from "./confirm";

export function useAppointmentText() {
  const { t, locale } = useI18n();

  // "Thursday 26 October 2026, 10:00 – 11:30", in the language displayed
  // and the time zone of the browser
  function when(appointment: Appointment): string {
    const day = new Intl.DateTimeFormat(locale.value, {
      weekday: "long",
      day: "numeric",
      month: "long",
      year: "numeric",
    });
    const time = new Intl.DateTimeFormat(locale.value, { hour: "2-digit", minute: "2-digit" });
    const start = new Date(appointment.starts_at);
    const end = new Date(appointment.ends_at);
    return `${day.format(start)}, ${time.format(start)} – ${time.format(end)}`;
  }

  // "Pending", "Accepted", "Declined", "Cancelled", "Expired"
  function state(value: AppointmentState): string {
    return t("appointments.state." + value);
  }

  return { when, state };
}

// The moves of the candidate and of the employer on an appointment
export function useAppointmentMoves(moved: (appointment: Appointment) => void) {
  const { t } = useI18n();
  const text = useAppointmentText();

  // The appointment whose move is in flight: its buttons are disabled meanwhile
  const busy = ref<number | null>(null);
  // The reason of a refused move, by appointment
  const errors = ref<Record<number, string>>({});

  // Runs one call of the API, keeps the answer or its reason
  async function run(appointment: Appointment, call: () => ReturnType<typeof cancelAppointment>): Promise<void> {
    delete errors.value[appointment.id];
    busy.value = appointment.id;
    try {
      const answer = await call();
      if (answer.status === 200 && answer.data) {
        moved(answer.data);
      } else {
        errors.value[appointment.id] = firstErrorOf(answer.data) || t("form.failed");
      }
    } catch {
      errors.value[appointment.id] = t("form.unreachable");
    } finally {
      busy.value = null;
    }
  }

  // The candidate accepts or declines, with a message
  async function answer(appointment: Appointment, accept: boolean): Promise<void> {
    const key = accept ? "accept" : "decline";
    const message = await confirmWithText(
      t(`appointments.confirm.${key}`, { when: text.when(appointment) }),
      t(`appointments.${key}`),
      t("appointments.answerLabel"),
      true,
    );
    if (message === null) return;
    await run(appointment, () => answerAppointment(appointment.id, accept, message));
  }

  // The employer cancels, with a word or not
  async function cancel(appointment: Appointment): Promise<void> {
    const message = await confirmWithText(
      t("appointments.confirm.cancel", { when: text.when(appointment) }),
      t("appointments.cancel"),
      t("appointments.cancelLabel"),
    );
    if (message === null) return;
    await run(appointment, () => cancelAppointment(appointment.id, message));
  }

  return { busy, errors, answer, cancel };
}
