// frontend/src/notifications.ts
//
// Notifications — the counts of the side bar, kept fresh
// ─────────────────────────────────────────────────────────────────────────────
// What the logged-in user has not seen yet, shared by every component: the
// messages not read, by kind of conversation (open, closed), and the
// applications that bring news (decisions of 22.10.2026: an application
// arriving for the employer, a move of its state for the candidate). The
// side bar shows them next to its links; a page that marks something seen
// asks for them again at once. Read from the API every minute while
// someone is logged in (phase 2: no WebSocket yet; phase 3 will push them
// and this file only will change).

import { reactive, readonly } from "vue";

import { unseenApplications } from "./api/applications";
import { unreadCounts } from "./api/messaging";

const counts = reactive({ open: 0, closed: 0, applications: 0 });

// How often the counts are read again, in milliseconds
const PERIOD = 60_000;
let timer = 0;

// Read-only view for the components
export function useNotifications() {
  return readonly(counts);
}

// Reads the counts now, both at once; a failure keeps the last ones
export async function refreshNotifications(): Promise<void> {
  try {
    const [messages, applications] = await Promise.all([unreadCounts(), unseenApplications()]);
    Object.assign(counts, { open: messages.open, closed: messages.closed, applications: applications.count });
  } catch {
    // Kept as they were; the next minute tries again
  }
}

// Starts reading the counts every minute (a user logged in), or stops and
// empties them (nobody)
export function followNotifications(loggedIn: boolean): void {
  window.clearInterval(timer);
  if (loggedIn) {
    refreshNotifications();
    timer = window.setInterval(refreshNotifications, PERIOD);
  } else {
    Object.assign(counts, { open: 0, closed: 0, applications: 0 });
  }
}
