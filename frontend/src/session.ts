// frontend/src/session.ts
//
// Session — who is logged in, shared by every component
// ─────────────────────────────────────────────────────────────────────────────
// One reactive object for the whole application, created once when this
// module is first imported. Components read it through useSession(); only
// the functions of this file change it, once the backend has answered.

import { reactive, readonly, watch } from "vue";

import {
  getSession,
  logIn,
  logOut,
  type SessionData,
  type User,
} from "./api/account";
import type { ApiResponse } from "./api/http";

type Session = {
  // The logged-in user, or null when nobody is
  user: User | null;
  // False until the backend has answered once: lets the pages wait instead
  // of showing the logged-out state for an instant at every start
  loaded: boolean;
};

const session = reactive<Session>({ user: null, loaded: false });

// Read-only view for the components: they cannot change it by accident
export function useSession() {
  return readonly(session);
}

// Settles once the backend has answered who is logged in. The router waits
// for it before showing a page meant for users, or for visitors only, so
// that a reload on such a page does not bounce while the answer is on its
// way. Settled already: answers at once.
export function whenLoaded(): Promise<void> {
  if (session.loaded) return Promise.resolve();
  return new Promise((resolve) => {
    const stop = watch(
      () => session.loaded,
      (loaded) => {
        if (loaded) {
          stop();
          resolve();
        }
      },
    );
  });
}

// Asks the backend who is logged in. Called once, when the application
// starts; a backend that cannot be reached counts as nobody logged in.
export async function loadSession(): Promise<void> {
  try {
    const answer = await getSession();
    session.user =
      answer.status === 200 && answer.data ? answer.data.user : null;
  } catch {
    session.user = null;
  }
  session.loaded = true;
}

// Logs in and keeps the user on success. The page gets the whole answer:
// a 400 carries the errors to display, a 401 means the address is not
// verified yet.
export async function login(
  email: string,
  password: string,
): Promise<ApiResponse<SessionData>> {
  const answer = await logIn(email, password);
  if (answer.status === 200 && answer.data) {
    session.user = answer.data.user;
  }
  return answer;
}

// Logs out and forgets the user
export async function logout(): Promise<void> {
  await logOut();
  session.user = null;
}
