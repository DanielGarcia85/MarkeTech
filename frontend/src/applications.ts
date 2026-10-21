// frontend/src/applications.ts
//
// Application texts and moves — what the pages of the applications share
// ─────────────────────────────────────────────────────────────────────────────
// The lines that the page of a candidate and the pages of an employer
// share: a date, the state, the history as one line. And, for the page of
// an employer, the move of an application from one state to the next,
// with its confirmation and its errors. Composables, because the
// words and the date formats depend on the language displayed.

import { ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";

import { setStatus, type Application, type ApplicationStatus } from "./api/applications";
import { firstErrorOf } from "./api/offers";
import { confirm } from "./confirm";

export function useApplicationText() {
  const { t, locale } = useI18n();

  // "20 October 2026", in the language displayed
  function date(iso: string): string {
    return new Intl.DateTimeFormat(locale.value, { dateStyle: "long" }).format(new Date(iso));
  }

  // "Received", "In progress", "Accepted", "Rejected"
  function status(value: ApplicationStatus): string {
    return t("applications.status." + value);
  }

  // "Received on 12 October · In progress on 14 October": every state the
  // application went through, with its day
  function history(application: Application): string {
    const day = new Intl.DateTimeFormat(locale.value, { day: "numeric", month: "long" });
    return application.history
      .map((change) => t("applications.historyStep", { status: status(change.status), date: day.format(new Date(change.changed_at)) }))
      .join(" · ");
  }

  // "Marie Dupont", as the employer's pages name a candidate
  function name(application: Application): string {
    return `${application.candidate.first_name} ${application.candidate.last_name}`.trim();
  }

  return { date, status, history, name };
}

// The moves of an employer on a list of applications: in progress at
// once, accepted or rejected after a confirmation; the answer replaces
// the application in the list, or its reason is kept to be shown under it
export function useApplicationMoves(applications: Ref<Application[] | null>) {
  const { t } = useI18n();
  const text = useApplicationText();

  // The application whose move is in flight: its buttons are disabled meanwhile
  const busy = ref<number | null>(null);
  // The reason of a refused move, by application
  const errors = ref<Record<number, string>>({});

  async function move(application: Application, status: ApplicationStatus): Promise<void> {
    if (status !== "in_progress") {
      const question = t(`receivedApplications.confirm.${status}`, { name: text.name(application) });
      if (!(await confirm(question, t(`receivedApplications.set.${status}`)))) return;
    }
    delete errors.value[application.id];
    busy.value = application.id;
    try {
      const answer = await setStatus(application.id, status);
      if (answer.status === 200 && answer.data) {
        applications.value = (applications.value ?? []).map((item) =>
          item.id === application.id ? answer.data! : item,
        );
      } else {
        errors.value[application.id] = firstErrorOf(answer.data) || t("form.failed");
      }
    } catch {
      errors.value[application.id] = t("form.unreachable");
    } finally {
      busy.value = null;
    }
  }

  return { busy, errors, move };
}
