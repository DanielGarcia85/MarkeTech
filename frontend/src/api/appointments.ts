// frontend/src/api/appointments.ts
//
// Appointments API — the meetings of the applications, as the backend serves them
// ─────────────────────────────────────────────────────────────────────────────
// The type of an appointment and one function per route: the appointments
// of an application (reading them marks the news seen), a proposal of the
// employer, the answer of the candidate, a cancellation by the employer,
// one's appointments over a period (the calendar), and the news of the side
// bar and of the cards.

import { getJson, send, type Answer } from "./http";

// The state the pages show: "expired" for a pending one that can no longer
// be answered (its time has come, or the application is decided)
export type AppointmentState = "pending" | "accepted" | "declined" | "cancelled" | "expired";

// The lengths offered, in minutes
export const DURATIONS = [30, 45, 60, 90] as const;

export type Appointment = {
  id: number;
  application: number;
  starts_at: string;
  ends_at: string;
  duration: number;
  place: string;
  note: string;
  state: AppointmentState;
  // The message of the candidate, or the word of the employer cancelling
  response: string;
  answered_at: string | null;
  created_at: string;
  // Its last change was news for the user, seen with this very reading
  new: boolean;
  // The offer, its company, the other participant (the company for the
  // candidate, the candidate for the employer)
  about: { offer: string; company: string; other: string };
};

export type Proposal = { starts_at: string; duration: number; place: string; note: string };

export type UnseenAppointments = { count: number; applications: Record<string, number> };

// The appointments of an application, in the order they take place
export function listAppointments(applicationId: number): Promise<Appointment[]> {
  return getJson<Appointment[]>(`/api/applications/${applicationId}/appointments/`);
}

// The employer proposes: 201 with the appointment, 400 with the errors
export function proposeAppointment(applicationId: number, proposal: Proposal): Promise<Answer<Appointment>> {
  return send<Appointment>("POST", `/api/applications/${applicationId}/appointments/`, proposal);
}

// The candidate accepts or declines, with a message
export function answerAppointment(id: number, accept: boolean, message: string): Promise<Answer<Appointment>> {
  return send<Appointment>("POST", `/api/appointments/${id}/answer/`, { accept, message });
}

// The employer cancels, with a word or not
export function cancelAppointment(id: number, message: string): Promise<Answer<Appointment>> {
  return send<Appointment>("POST", `/api/appointments/${id}/cancel/`, { message });
}

// One's appointments starting between start (included) and end (excluded),
// both as ISO times
export function myAppointments(start: string, end?: string): Promise<Appointment[]> {
  const query = new URLSearchParams({ start });
  if (end) query.set("end", end);
  return getJson<Appointment[]>(`/api/appointments/?${query}`);
}

export function unseenAppointments(): Promise<UnseenAppointments> {
  return getJson<UnseenAppointments>("/api/appointments/unseen/");
}
