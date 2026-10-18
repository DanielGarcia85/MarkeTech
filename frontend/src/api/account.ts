// frontend/src/api/account.ts
//
// Account API — one function per call of the authentication API
// ─────────────────────────────────────────────────────────────────────────────
// Names each endpoint of allauth once, with the shape of what it receives and
// returns. Pages and the session never write a path or a field name
// themselves: they call these functions.

import { api, type ApiResponse } from "./http";

// The two roles a visitor can pick at sign-up (an administrator has none)
export type Role = "candidate" | "employer";

// The user as the authentication API describes it
export type User = {
  id: number;
  email: string;
  display: string;
  has_usable_password: boolean;
  role: Role | "";
};

// Answer of the calls that may open a session: the user, when logged in
export type SessionData = { user: User };

// Who is logged in: status 200 with the user, or 401 with nobody
export function getSession(): Promise<ApiResponse<SessionData>> {
  return api("GET", "auth/session");
}

// What the sign-up form collects. Named fields rather than a list of
// strings: the first and last name could not be told apart otherwise
export type SignupData = {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: Role;
};

// Creates the account; 401 afterwards, because the address must be verified.
// The API names the fields as the backend does, with underscores.
export function signUp(data: SignupData): Promise<ApiResponse<SessionData>> {
  return api("POST", "auth/signup", {
    email: data.email,
    password: data.password,
    first_name: data.firstName,
    last_name: data.lastName,
    role: data.role,
  });
}

// Opens the session: 200 with the user, 400 with errors, 401 if the address
// is not verified yet
export function logIn(
  email: string,
  password: string,
): Promise<ApiResponse<SessionData>> {
  return api("POST", "auth/login", { email, password });
}

// Closes the session; answers 401, which here means "done"
export function logOut(): Promise<ApiResponse<SessionData>> {
  return api("DELETE", "auth/session");
}

// Confirms the address with the key read from the link of the e-mail
export function verifyEmail(key: string): Promise<ApiResponse<SessionData>> {
  return api("POST", "auth/email/verify", { key });
}

// Asks for the reset e-mail; always 200, to reveal nothing about the address
export function requestPasswordReset(
  email: string,
): Promise<ApiResponse<unknown>> {
  return api("POST", "auth/password/request", { email });
}

// Sets the new password with the key read from the link of the e-mail
export function resetPassword(
  key: string,
  password: string,
): Promise<ApiResponse<SessionData>> {
  return api("POST", "auth/password/reset", { key, password });
}

// ── Changes made by a logged-in user, from the profile page ───────────

// One address of the account, as the authentication API lists them: the
// current one (verified, primary) and, while a change is pending, the new
// one, not verified yet
export type EmailAddressInfo = {
  email: string;
  verified: boolean;
  primary: boolean;
};

// The addresses of the account: 200 with the list
export function listEmails(): Promise<ApiResponse<EmailAddressInfo[]>> {
  return api("GET", "account/email");
}

// Asks to use a new address. A confirmation e-mail goes to it, and the
// current address stays in force until the link is opened. 200 with the
// list, the new address in it unverified; 400 with the errors of the field
// (invalid, or already the address of the account)
export function changeEmail(
  email: string,
): Promise<ApiResponse<EmailAddressInfo[]>> {
  return api("POST", "account/email", { email });
}

// Drops the new address before it is confirmed: 200 with the list
export function cancelEmailChange(
  email: string,
): Promise<ApiResponse<EmailAddressInfo[]>> {
  return api("DELETE", "account/email", { email });
}

// Replaces the password, the current one proving who asks. 200 with the
// user, the session kept open; 400 with the errors of either field
export function changePassword(
  currentPassword: string,
  newPassword: string,
): Promise<ApiResponse<SessionData>> {
  return api("POST", "account/password/change", {
    current_password: currentPassword,
    new_password: newPassword,
  });
}
