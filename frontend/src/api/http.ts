// frontend/src/api/http.ts
//
// HTTP client — the only place where the frontend talks to the backend
// ─────────────────────────────────────────────────────────────────────────────
// Components never call the browser's fetch function themselves: they go
// through the functions of this file, so that the way requests are sent can
// change here without touching the rest of the application.
//
// Three kinds of calls. getJson reads our own API, which answers plain JSON.
// send writes to it: JSON or a form with files, and the answer comes back
// with its status, because a 400 carries the errors of the fields. api talks
// to the authentication API of allauth, which always answers an envelope
// { status, data, errors, meta }, even with a 400 or 401 status: there, those
// are ordinary answers (a field is invalid, nobody is logged in).

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

// Sorts the errors of a 400 answer by field, for a form to display each one
// under its field: the key is the param, or "" for an error about the whole
// request. Only the first message of each field is kept.
export function errorsByParam(
  errors: ApiError[] = [],
): Record<string, string> {
  const byParam: Record<string, string> = {};
  for (const error of errors) {
    const key = error.param ?? "";
    if (!(key in byParam)) {
      byParam[key] = error.message;
    }
  }
  return byParam;
}

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

// Answer of a call that writes to our API: the status, and the JSON body
// when there is one (null after a 204). With a 400, the body is the errors
// of DRF: { "field": ["message", ...] }
export type Answer<T> = { status: number; data: T | null };

// Errors of a 400 answer of our API, one message per field: the first one
// of each list. The key "" is kept for an error about the whole request.
export function firstErrors(
  data: Record<string, string[]> | null,
): Record<string, string> {
  const errors: Record<string, string> = {};
  for (const [field, messages] of Object.entries(data ?? {})) {
    const key = field === "non_field_errors" || field === "detail" ? "" : field;
    const message = Array.isArray(messages) ? messages[0] : String(messages);
    if (message !== undefined && !(key in errors)) {
      errors[key] = message;
    }
  }
  return errors;
}

// Writes to our API and returns the answer, whatever the status. A FormData
// body is sent as a form with files (the browser sets its content type); any
// other body is sent as JSON.
export async function send<T>(
  method: "PATCH" | "POST" | "DELETE",
  path: string,
  body?: FormData | object,
): Promise<Answer<T>> {
  const headers = commonHeaders();
  headers["X-CSRFToken"] = csrfToken();
  let payload: BodyInit | undefined;
  if (body instanceof FormData) {
    payload = body;
  } else if (body !== undefined) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  const response = await fetch(path, { method, headers, body: payload });
  const data =
    response.status === 204 ? null : ((await response.json()) as T);
  return { status: response.status, data };
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
