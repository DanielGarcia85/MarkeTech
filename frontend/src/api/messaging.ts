// frontend/src/api/messaging.ts
//
// Messaging API — the conversations of the applications, as the backend serves them
// ─────────────────────────────────────────────────────────────────────────────
// The types of a conversation and of a message, and one function per route:
// one's conversations (open or closed), the conversation of an application
// (reading it marks the other's messages read), writing in it, and the
// unread counts of the side bar. The message that comes with a move of the
// state is sent by setStatus (api/applications.ts).

import type { ApplicationStatus } from "./applications";
import { getJson, send, type Answer } from "./http";

// What the list and the page of a conversation show of it
export type ConversationHead = {
  application: number;
  status: ApplicationStatus;
  // Whether one may write: the application is in progress
  open: boolean;
  offer: { id: number; title: string; company: { name: string; logo: string | null } };
  // The company for the candidate, the candidate for the employer
  other: string;
};

// One message; "mine" when the logged-in user wrote it
export type Message = {
  id: number;
  body: string;
  sent_at: string;
  read_at: string | null;
  mine: boolean;
};

// A conversation in the list: its head, its last message, its unread
export type Conversation = ConversationHead & {
  last: { body: string; sent_at: string; mine: boolean };
  unread: number;
};

// The conversation of an application, its messages oldest first
export type Thread = ConversationHead & { messages: Message[] };

export type UnreadCounts = { count: number; open: number; closed: number };

// One's conversations, the most recent activity first; "open" or "closed"
// for one kind only
export function listConversations(state?: "open" | "closed"): Promise<Conversation[]> {
  return getJson<Conversation[]>("/api/messages/" + (state ? `?state=${state}` : ""));
}

// The conversation of an application; 404 when it is not one's own
export function getThread(applicationId: number): Promise<Thread> {
  return getJson<Thread>(`/api/applications/${applicationId}/messages/`);
}

// Write in it: 201 with the message, 400 when the application is not in
// progress or the text is empty or too long
export function writeMessage(applicationId: number, body: string): Promise<Answer<Message>> {
  return send<Message>("POST", `/api/applications/${applicationId}/messages/`, { body });
}

export function unreadCounts(): Promise<UnreadCounts> {
  return getJson<UnreadCounts>("/api/messages/unread/");
}
