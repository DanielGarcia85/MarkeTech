// frontend/src/api/http.ts
//
// HTTP client — the only place where the frontend talks to the backend
// ─────────────────────────────────────────────────────────────────────────────
// Components never call the browser's fetch function themselves: they go
// through the functions of this file, so that the way requests are sent can
// change here without touching the rest of the application.
//
// Two kinds of calls. getJson talks to our own API, which answers plain JSON.
// api talks to the authentication API of allauth, which always answers an
// envelope { status, data, errors, meta }, even with a 400 or 401 status:
// there, those are ordinary answers (a field is invalid, nobody is logged in).

import { i18n } from "../i18n";

// Base address of the authentication API: the browser client of allauth
export const AUTH_API = "/_allauth/browser/v1/";

// One error of the authentication API: about one field (param) or, without
// param, about the whole request
export type ApiError = { message: string; code: string; param?: string };

// Envelope of every answer of the authentication API
export type ApiResponse<T> = {
  status: number;
  data?: T;
  errors?: ApiError[];
  meta?: { is_authenticated?: boolean };
};

// Headers sent with every request
function commonHeaders(): Record<string, string> {
  return {
    Accept: "application/json",
    // Language shown by the interface: the backend answers, and writes its
    // e-mails, in that language
    "Accept-Language": i18n.global.locale.value,
  };
}

// Value of the CSRF cookie set by Django. Sent back as a header with every
// request that changes something: Django refuses the request without it.
function csrfToken(): string {
  const prefix = "csrftoken=";
  const cookie = document.cookie
    .split("; ")
    .find((item) => item.startsWith(prefix));
  return cookie ? cookie.slice(prefix.length) : "";
}

// Sends a GET request to our API and returns its JSON answer.
// T is the shape the caller expects for that answer.
export async function getJson<T>(path: string): Promise<T> {
  const response = await fetch(path, { headers: commonHeaders() });

  // fetch only fails when the server cannot be reached: an error status
  // such as 404 or 500 has to be turned into an error here
  if (!response.ok) {
    throw new Error(`Request to ${path} failed with status ${response.status}`);
  }

  return (await response.json()) as T;
}

// Calls the authentication API and returns its envelope, whatever the status.
// path is relative to AUTH_API; body, when given, is sent as JSON.
export async function api<T>(
  method: "GET" | "POST" | "DELETE",
  path: string,
  body?: unknown,
): Promise<ApiResponse<T>> {
  const headers = commonHeaders();
  if (method !== "GET") {
    headers["X-CSRFToken"] = csrfToken();
  }
  if (body !== undefined) {
    headers["Content-Type"] = "application/json";
  }

  const response = await fetch(AUTH_API + path, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  return (await response.json()) as ApiResponse<T>;
}
