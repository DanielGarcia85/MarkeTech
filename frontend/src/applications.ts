// frontend/src/applications.ts
//
// Application texts and moves — what the pages of the applications share
// ─────────────────────────────────────────────────────────────────────────────
// The lines that the page of a candidate and the pages of an employer
// share: a date, the state, the history as one line. And, for the page of
// an employer, the move of an application from one state to the next,
// with its confirmation, the message that may go with it, and its errors. Composables, because the
// words and the date formats depend on the language displayed. Last, the
// mark of the news, kept for the whole visit of a page.

import { ref, type Ref } from "vue";
import { useI18n } from "vue-i18n";

import { setStatus, type Application, type ApplicationStatus } from "./api/applications";
import { firstErrorOf } from "./api/offers";
import { confirmWithText } from "./confirm";

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

// The moves of an employer on a list of applications, each after a
// confirmation that offers an optional message: the first of the
// conversation when the application goes in progress, the last one with a
// decision (decisions of 21.10.2026). The answer replaces the application
// in the list, or its reason is kept to be shown under it; "moved" is
// called after a move that wrote a message (the page counts the
// conversations again)
export function useApplicationMoves(applications: Ref<Application[] | null>, moved?: () => void) {
  const { t } = useI18n();
  const text = useApplicationText();

  // The application whose move is in flight: its buttons are disabled meanwhile
  const busy = ref<number | null>(null);
  // The reason of a refused move, by application
  const errors = ref<Record<number, string>>({});

  async function move(application: Application, status: ApplicationStatus): Promise<void> {
    const question = t(`receivedApplications.confirm.${status}`, { name: text.name(application) });
    const label = t(status === "in_progress" ? "receivedApplications.firstMessage" : "receivedApplications.lastMessage");
    const message = await confirmWithText(question, t(`receivedApplications.set.${status}`), label);
    if (message === null) return;
    delete errors.value[application.id];
    busy.value = application.id;
    try {
      const answer = await setStatus(application.id, status, message);
      if (answer.status === 200 && answer.data) {
        applications.value = (applications.value ?? []).map((item) =>
          item.id === application.id ? answer.data! : item,
        );
        if (message) moved?.();
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

// Keeps the mark of the news ("New", "Updated") on an application for the
// whole visit of a page: the API marks the news seen at the first reading,
// and the page reads again at each news of the WebSocket (live.ts).
// Returns the function that a list goes through after each reading
export function keepNews(): (list: Application[]) => Application[] {
  const news = new Set<number>();
  return (list) => {
    for (const item of list) if (item.unseen) news.add(item.id);
    return list.map((item) => (news.has(item.id) ? { ...item, unseen: true } : item));
  };
}
