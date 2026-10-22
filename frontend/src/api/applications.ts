// frontend/src/api/applications.ts
//
// Applications API — the job applications, as the backend serves them
// ─────────────────────────────────────────────────────────────────────────────
// The type of an application, what a candidate sends to apply, and one
// function per route: the list of one's own (a candidate's, or those to an
// employer's offers), applying, withdrawing, moving the state. The states
// are the values stored by the backend; their texts are in the language
// files, under applications.status.*.

import { getJson, send, type Answer } from "./http";
import type { OfferStatus } from "./offers";

// ── Types ─────────────────────────────────────────────────────────────

export type ApplicationStatus = "received" | "in_progress" | "accepted" | "rejected";

// What an employer may set, in the order the buttons show them; received
// is the state of a new application only
export const EMPLOYER_STATUSES: ApplicationStatus[] = ["in_progress", "accepted", "rejected"];

// A file of an application: its name, and the URL of the API that serves
// it to the candidate and to the employer of the offer
export type ApplicationFile = { name: string; url: string };

export type Attachment = ApplicationFile & { id: number };

// An application as the API gives it. The offer and the candidate are read
// at the time of the answer, never copied; a date is an ISO string.
export type Application = {
  id: number;
  offer: {
    id: number;
    title: string;
    city: string;
    status: OfferStatus;
    company: { name: string };
  };
  candidate: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    city: string;
  };
  cv: ApplicationFile;
  cover_letter: ApplicationFile | null;
  attachments: Attachment[];
  status: ApplicationStatus;
  // Every state the application went through, oldest first
  history: { status: ApplicationStatus; changed_at: string }[];
  created_at: string;
  updated_at: string;
};

// What a candidate sends to apply: the offer, a CV file or the one of the
// profile, an optional letter, and the documents of the profile to join
export type ApplicationInput = {
  offer: number;
  cv: File | null;
  useProfileCv: boolean;
  coverLetter: File | null;
  documents: number[];
};

// Withdrawing is allowed until the employer decides
export function canWithdraw(application: Application): boolean {
  return application.status === "received" || application.status === "in_progress";
}

// ── Reading ───────────────────────────────────────────────────────────

// One's own applications, newest first: a candidate's, or those to the
// offers of an employer; narrowed to one offer, or to one state
export function listApplications(filters: { offer?: number; status?: ApplicationStatus } = {}): Promise<Application[]> {
  const params = new URLSearchParams();
  if (filters.offer) params.set("offer", String(filters.offer));
  if (filters.status) params.set("status", filters.status);
  const query = params.toString();
  return getJson<Application[]>("/api/applications/" + (query ? "?" + query : ""));
}

// ── Applying and withdrawing, for a candidate ─────────────────────────
// Every call answers with its status: a 400 carries the errors by field
// (or under non_field_errors), a 403 means the account is not a candidate,
// a 404 that the application is somebody else's

// Apply: a form with the files, as the backend reads it (the documents as
// a repeated field)
export function apply(input: ApplicationInput): Promise<Answer<Application>> {
  const form = new FormData();
  form.append("offer", String(input.offer));
  if (input.useProfileCv) {
    form.append("use_profile_cv", "true");
  } else if (input.cv) {
    form.append("cv", input.cv);
  }
  if (input.coverLetter) form.append("cover_letter", input.coverLetter);
  for (const id of input.documents) form.append("documents", String(id));
  return send<Application>("POST", "/api/applications/", form);
}

// Withdraw: refused once the employer decided
export function withdraw(id: number): Promise<Answer<null>> {
  return send<null>("DELETE", `/api/applications/${id}/`);
}

// ── The state, for an employer ────────────────────────────────────────

// in_progress, accepted or rejected; the backend records the history. A
// message, when given, goes to the conversation of the application: the
// first one when it goes in progress, the last one with a decision
export function setStatus(
  id: number,
  status: ApplicationStatus,
  message = "",
): Promise<Answer<Application>> {
  return send<Application>("POST", `/api/applications/${id}/status/`, { status, message });
}
