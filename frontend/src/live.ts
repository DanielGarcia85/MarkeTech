// frontend/src/live.ts
//
// Live — the WebSocket of the logged-in user, and the news it brings
// ─────────────────────────────────────────────────────────────────────────────
// One connection per tab while someone is logged in, to /ws/ on the same
// address as the page (backend/live, decisions of 26.10.2026). The server
// sends a signal, never the data: { type: "messages", application: 12 }
// says that something changed in the messages of application 12; whoever
// shows them reads again through the API. A component that cares listens
// with onNews().
//
// Nothing must be missed while the line is down: each time it opens (the
// first time, and after a cut), and each time the tab comes back to the
// front, the listeners hear "everything" (null) and read all they show
// again. A cut line opens again by itself, after 1 s, then 2, 4… up to
// 30 s between two tries. Logging out closes it; another user opens a new
// one, with their own session.

// The kinds of news, as the server sends them (backend/live/notify.py)
export type Kind = "messages" | "applications" | "appointments";

// A signal: something of this kind changed in this application
export type Signal = { type: Kind; application: number };

// What a listener hears: a signal, or null for "read everything again"
export type Listener = (signal: Signal | null) => void;

const listeners = new Set<Listener>();

// The connection of this tab, and the user it belongs to
let socket: WebSocket | null = null;
let user: number | undefined;

// The wait before the next try after a cut, in milliseconds, and the
// timer of that try
const FIRST_DELAY = 1_000;
const LONGEST_DELAY = 30_000;
let delay = FIRST_DELAY;
let retry = 0;

// Listens to the news; returns the function that stops listening, to call
// when the component goes away (onUnmounted)
export function onNews(listener: Listener): () => void {
  listeners.add(listener);
  return () => listeners.delete(listener);
}

function tell(signal: Signal | null): void {
  listeners.forEach((listener) => listener(signal));
}

// The address of the WebSocket: the host of the page, wss: when the page
// came over https:
function address(): string {
  const scheme = window.location.protocol === "https:" ? "wss:" : "ws:";
  return `${scheme}//${window.location.host}/ws/`;
}

function open(): void {
  const current = new WebSocket(address());
  socket = current;
  current.onopen = () => {
    delay = FIRST_DELAY;
    // Whatever happened while the line was down
    tell(null);
  };
  current.onmessage = (event) => {
    try {
      tell(JSON.parse(event.data) as Signal);
    } catch {
      // Not a signal: ignored
    }
  };
  current.onclose = () => {
    // A connection closed on purpose (logging out, another user) is no
    // longer the current one: nothing to do
    if (socket !== current) return;
    socket = null;
    retry = window.setTimeout(open, delay);
    delay = Math.min(delay * 2, LONGEST_DELAY);
  };
}

// Follows whoever is logged in (their id, or undefined for nobody): opens
// the connection, closes it, or replaces it by one with the new session
export function followLive(id: number | undefined): void {
  if (id === user) return;
  user = id;
  window.clearTimeout(retry);
  const previous = socket;
  socket = null;
  previous?.close();
  delay = FIRST_DELAY;
  if (id !== undefined) open();
}

// Back to the front after a while in the background, or after the computer
// slept: read everything again, and try again at once if the line is down
document.addEventListener("visibilitychange", () => {
  if (document.visibilityState !== "visible" || user === undefined) return;
  if (socket) {
    tell(null);
  } else {
    window.clearTimeout(retry);
    delay = FIRST_DELAY;
    open();
  }
});
