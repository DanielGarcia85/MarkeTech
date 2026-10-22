// frontend/src/api/demo.ts
//
// Demo API — opening a demo account without its password
// ─────────────────────────────────────────────────────────────────────────────
// The one call behind the buttons "Try the demo" of the login page: the
// backend opens the session of the demo account of a role, the terms of use
// accepted (decisions of 22.10.2026). 200 once open, 400 without the terms,
// 404 when the database has no demo account.

import type { Role } from "./account";
import { send, type Answer } from "./http";

export function demoLogin(role: Role): Promise<Answer<{ email: string; role: Role }>> {
  return send<{ email: string; role: Role }>("POST", "/api/demo/login/", { role, terms: true });
}
