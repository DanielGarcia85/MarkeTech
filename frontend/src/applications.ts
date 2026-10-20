// frontend/src/applications.ts
//
// Application texts — how an application is written on the pages
// ─────────────────────────────────────────────────────────────────────────────
// The lines that the page of a candidate and the page of an employer
// share: a date, the state, the history as one line. A composable, because
// the words and the date formats depend on the language displayed.

import { useI18n } from "vue-i18n";

import type { Application, ApplicationStatus } from "./api/applications";

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

  return { date, status, history };
}
