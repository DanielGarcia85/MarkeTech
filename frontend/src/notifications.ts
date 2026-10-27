// frontend/src/notifications.ts
//
// Notifications — the counts of the side bar, kept fresh
// ─────────────────────────────────────────────────────────────────────────────
// What the logged-in user has not seen yet, shared by every component: the
// messages not read, by kind of conversation (open, closed), and the
// applications that bring news (decisions of 22.10.2026: an application
// arriving for the employer, a move of its state for the candidate) and the
// appointments that do (a proposal or a cancellation for the candidate, an
// answer for the employer), in all and by application. The
// side bar shows them next to its links; a page that marks something seen
// asks for them again at once. Read from the API when someone logs in,
// then again at each news the WebSocket brings, and after a cut (live.ts,
// decisions of 26.10.2026): no timer.

import { reactive, readonly } from "vue";

import { unseenApplications } from "./api/applications";
import { unseenAppointments } from "./api/appointments";
import { unreadCounts } from "./api/messaging";
import { onNews } from "./live";

// byApplication: the appointments that are news, by application id, for
// the Messages buttons of the cards
const counts = reactive({
  open: 0,
  closed: 0,
  applications: 0,
  appointments: 0,
  byApplication: {} as Record<string, number>,
});

// Read-only view for the components
export function useNotifications() {
  return readonly(counts);
}

// What the Messages button of an application card counts: the unread
// messages of its conversation (undefined when it has none) and its
// appointments that are news; undefined when there is neither
export function newsOf(unread: number | undefined, applicationId: number): number | undefined {
  const appointments = counts.byApplication[String(applicationId)] ?? 0;
  if (unread === undefined && appointments === 0) return undefined;
  return (unread ?? 0) + appointments;
}

// Reads the counts now, all at once; a failure keeps the last ones
export async function refreshNotifications(): Promise<void> {
  try {
    const [messages, applications, appointments] = await Promise.all([
      unreadCounts(),
      unseenApplications(),
      unseenAppointments(),
    ]);
    Object.assign(counts, {
      open: messages.open,
      closed: messages.closed,
      applications: applications.count,
      appointments: appointments.count,
      byApplication: appointments.applications,
    });
  } catch {
    // Kept as they were; the next news tries again
  }
}

// Reads the counts for a user who logs in, or empties them (nobody)
export function followNotifications(loggedIn: boolean): void {
  if (loggedIn) {
    refreshNotifications();
  } else {
    Object.assign(counts, { open: 0, closed: 0, applications: 0, appointments: 0, byApplication: {} });
  }
}

// Any news may change a count, and so may what happened during a cut:
// read them all again. The WebSocket is open only while someone is logged
// in, so no news comes for nobody
onNews(() => refreshNotifications());
