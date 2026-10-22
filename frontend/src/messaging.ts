// frontend/src/messaging.ts
//
// Unread messages — the counts of the side bar, kept fresh
// ─────────────────────────────────────────────────────────────────────────────
// The number of messages the logged-in user has not read, in all and by
// kind of conversation (open, closed), shared by every component: the side
// bar shows them, the page of a conversation asks for them again once it
// has marked its messages read. Read from the API every minute while
// someone is logged in (phase 2: no WebSocket yet; phase 3 will push them
// and this file only will change).

import { reactive, readonly } from "vue";

import { unreadCounts, type UnreadCounts } from "./api/messaging";

const counts = reactive<UnreadCounts>({ count: 0, open: 0, closed: 0 });

// How often the counts are read again, in milliseconds
const PERIOD = 60_000;
let timer = 0;

// Read-only view for the components
export function useUnread() {
  return readonly(counts);
}

// Reads the counts now; a failure keeps the last ones
export async function refreshUnread(): Promise<void> {
  try {
    Object.assign(counts, await unreadCounts());
  } catch {
    // Kept as they were; the next minute tries again
  }
}

// Starts reading the counts every minute (a user logged in), or stops and
// empties them (nobody)
export function followUnread(loggedIn: boolean): void {
  window.clearInterval(timer);
  if (loggedIn) {
    refreshUnread();
    timer = window.setInterval(refreshUnread, PERIOD);
  } else {
    Object.assign(counts, { count: 0, open: 0, closed: 0 });
  }
}
