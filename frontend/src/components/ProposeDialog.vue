<!--
  frontend/src/components/ProposeDialog.vue

  Proposal dialog — the form an employer fills in to propose an appointment
  ───────────────────────────────────────────────────────────────────────────
  Opened by ConversationPage from its "Propose an appointment" button, for
  the employer of an application in progress. A box over the greyed page,
  as the confirmation dialog: the day and the time (the browser's own
  picker, in its time zone, never in the past), the length (30, 45, 60 or
  90 minutes), where or how (an address, a link to a video call, "by
  phone") and a note if the employer wishes. Sent to the API, which checks
  it again; its errors are shown under their field. Emits the appointment
  created, or "close" when given up (Cancel, Escape, a click outside).
-->

<script setup lang="ts">
import { nextTick, onMounted, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";

import { DURATIONS, proposeAppointment, type Appointment } from "../api/appointments";
import { firstErrors } from "../api/http";

const props = defineProps<{ applicationId: number }>();
const emit = defineEmits<{ proposed: [appointment: Appointment]; close: [] }>();

const { t } = useI18n();

const box = ref<HTMLDialogElement | null>(null);
const form = reactive({ when: "", duration: 60, place: "", note: "" });
const errors = ref<Record<string, string>>({});
const sending = ref(false);

// "2026-10-22T16:30", the format of a datetime-local field, in the time
// zone of the browser: the earliest time it offers is now
function local(date: Date): string {
  const shifted = new Date(date.getTime() - date.getTimezoneOffset() * 60_000);
  return shifted.toISOString().slice(0, 16);
}
const earliest = local(new Date());

onMounted(async () => {
  await nextTick();
  box.value?.showModal();
});

function clickOutside(event: MouseEvent): void {
  if (event.target === box.value) emit("close");
}

async function submit(): Promise<void> {
  errors.value = {};
  if (!form.when) {
    errors.value = { starts_at: t("appointments.form.whenMissing") };
    return;
  }
  sending.value = true;
  try {
    // The time typed is local: the API receives it with its offset (ISO)
    const answer = await proposeAppointment(props.applicationId, {
      starts_at: new Date(form.when).toISOString(),
      duration: form.duration,
      place: form.place,
      note: form.note,
    });
    if (answer.status === 201 && answer.data) {
      emit("proposed", answer.data);
    } else {
      errors.value = firstErrors(answer.data as Record<string, string[]> | null);
      if (Object.keys(errors.value).length === 0) errors.value = { "": t("form.failed") };
    }
  } catch {
    errors.value = { "": t("form.unreachable") };
  } finally {
    sending.value = false;
  }
}
</script>

<template>
  <dialog ref="box" class="propose" @cancel.prevent="emit('close')" @click="clickOutside">
    <form class="box" novalidate @submit.prevent="submit">
      <h2>{{ t("appointments.form.title") }}</h2>
      <p v-if="errors['']" class="error">{{ errors[""] }}</p>
      <div class="row">
        <div class="field">
          <label for="appointment-when">{{ t("appointments.form.when") }}</label>
          <input id="appointment-when" v-model="form.when" type="datetime-local" :min="earliest" step="300" />
          <p v-if="errors.starts_at" class="error">{{ errors.starts_at }}</p>
        </div>
        <div class="field">
          <label for="appointment-duration">{{ t("appointments.form.duration") }}</label>
          <select id="appointment-duration" v-model.number="form.duration">
            <option v-for="minutes in DURATIONS" :key="minutes" :value="minutes">
              {{ t("appointments.duration." + minutes) }}
            </option>
          </select>
          <p v-if="errors.duration" class="error">{{ errors.duration }}</p>
        </div>
      </div>
      <div class="field">
        <label for="appointment-place">{{ t("appointments.form.place") }}</label>
        <input
          id="appointment-place"
          v-model="form.place"
          type="text"
          maxlength="200"
          :placeholder="t('appointments.form.placeHint')"
        />
        <p v-if="errors.place" class="error">{{ errors.place }}</p>
      </div>
      <div class="field">
        <label for="appointment-note">{{ t("appointments.form.note") }}</label>
        <textarea id="appointment-note" v-model="form.note" rows="3" maxlength="2000"></textarea>
        <p v-if="errors.note" class="error">{{ errors.note }}</p>
      </div>
      <p class="choices">
        <button type="button" class="secondary" @click="emit('close')">{{ t("dialog.cancel") }}</button>
        <button type="submit" class="primary" :disabled="sending">{{ t("appointments.form.send") }}</button>
      </p>
    </form>
  </dialog>
</template>

<style scoped>
/* The <dialog> fills the window and carries the grey veil; the box sits
   in its middle, as the confirmation dialog */
.propose {
  width: 100%;
  max-width: none;
  height: 100%;
  max-height: none;
  margin: 0;
  padding: 16px;
  border: none;
  background: transparent;
}

.propose::backdrop {
  background: rgba(30, 41, 59, 0.45);
}

.box {
  max-width: 560px;
  margin: 10vh auto 0;
  padding: 20px 24px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  background: var(--mt-background);
  box-shadow: 0 16px 40px rgba(30, 41, 59, 0.2);
}

h2 {
  margin: 0 0 16px;
  color: var(--mt-blue);
  font-size: 1.25rem;
}

/* The day and the length side by side, one under the other when narrow */
.row {
  display: grid;
  grid-template-columns: minmax(0, 3fr) minmax(0, 2fr);
  gap: 0 16px;
}

.box .field input,
.box .field select,
.box .field textarea {
  display: block;
  width: 100%;
  max-width: none;
  padding: 8px;
  border: 1px solid var(--mt-border);
  border-radius: 6px;
  background: var(--mt-background);
  color: var(--mt-text);
  font: inherit;
}

.field textarea {
  resize: vertical;
}

/* Cancel first, the action last, on the right */
.choices {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  margin: 0;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 6px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}

@media (max-width: 520px) {
  .row {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
