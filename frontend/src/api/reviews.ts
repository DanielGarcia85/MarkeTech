// frontend/src/api/reviews.ts
//
// Reviews API — what the users think of the platform, as the backend serves it
// ─────────────────────────────────────────────────────────────────────────────
// The types of a review and of the summary of all of them, and one function
// per route: the public list with its summary, one's own review, writing or
// rewriting it, deleting it.

import { getJson, getJsonOrNull, send, type Answer } from "./http";

// The four detailed scores, in the order the pages show them
export const CRITERIA = ["ease_of_use", "offers_and_applications", "messaging", "appointments"] as const;
export type Criterion = (typeof CRITERIA)[number];

// The overall rating and the four detailed scores, from 1 to 5
export type Scores = Record<"rating" | Criterion, number>;

// A review as the API gives it. The author as the public sees them: first
// name and initial (null without a first name), role, company of an
// employer
export type Review = Scores & {
  id: number;
  comment: string;
  created_at: string;
  updated_at: string;
  author: { name: string | null; role: "candidate" | "employer"; company: string | null };
  // The review of the user asking
  mine: boolean;
};

// All the reviews at once: how many, the average of each score (null
// without reviews), how many gave each rating ("5" to "1")
export type Summary = {
  count: number;
  averages: Record<"rating" | Criterion, number | null>;
  ratings: Record<string, number>;
};

// A page of the list, with the summary of every review
export type ReviewPage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Review[];
  summary: Summary;
};

// What an author sends
export type ReviewForm = Scores & { comment: string };

// The reviews, newest first: page by page, ten by default
export function listReviews(page = 1, pageSize = 10): Promise<ReviewPage> {
  return getJson<ReviewPage>(`/api/reviews/?page=${page}&page_size=${pageSize}`);
}

// One's review, null before it is written
export function getMyReview(): Promise<Review | null> {
  return getJsonOrNull<Review>("/api/reviews/mine/");
}

// Write or rewrite one's review: 201 or 200, 400 with the errors of the
// fields, 403 for a demo account
export function saveMyReview(form: ReviewForm): Promise<Answer<Review>> {
  return send<Review>("PUT", "/api/reviews/mine/", form);
}

// Delete one's review: 204
export function deleteMyReview(): Promise<Answer<null>> {
  return send<null>("DELETE", "/api/reviews/mine/");
}
