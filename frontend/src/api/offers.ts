// frontend/src/api/offers.ts
//
// Offers API — the job offers, as the backend serves them
// ─────────────────────────────────────────────────────────────────────────────
// The types of an offer and of a page of offers, the filters of the public
// list, what an employer writes in an offer, and one function per route:
// the public reading, then the management by an employer. The choices
// (contract, remote work, salary period, currency, status) are the values
// stored by the backend; their texts are in the language files, under
// offers.*.

import { firstErrors, getJson, send, type Answer } from "./http";

// ── Types ─────────────────────────────────────────────────────────────

export type Contract = "permanent" | "fixed_term" | "internship" | "student";
export type Remote = "on_site" | "hybrid" | "remote";
export type SalaryPeriod = "month" | "year";
export type Currency = "CHF" | "EUR";
export type OfferStatus = "draft" | "published" | "closed";

// The lists of the choices, in the order the forms and the filters show them
export const CONTRACTS: Contract[] = ["permanent", "fixed_term", "internship", "student"];
export const REMOTES: Remote[] = ["on_site", "hybrid", "remote"];
export const SALARY_PERIODS: SalaryPeriod[] = ["month", "year"];
export const CURRENCIES: Currency[] = ["CHF", "EUR"];

// Offers by page of the public list, as the backend paginates them
export const PAGE_SIZE = 10;

// An offer as the API gives it. The company is read on the profile of the
// employer at the time of the answer: its name, and the URL of its logo or
// null. The country is its two-letter code; a date is an ISO string.
export type Offer = {
  id: number;
  title: string;
  description: string;
  city: string;
  country: string;
  remote: Remote;
  contract: Contract;
  workload_min: number | null;
  workload_max: number | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_period: SalaryPeriod;
  currency: Currency;
  experience_years: number | null;
  status: OfferStatus;
  published_at: string | null;
  created_at: string;
  updated_at: string;
  company: { name: string; logo: string | null };
};

// One page of the public list, as the backend paginates it
export type OfferPage = {
  count: number;
  next: string | null;
  previous: string | null;
  results: Offer[];
};

// The filters of the public list; an empty string means "no filter". The
// keys are the parameters of the API, so that they go straight into the
// query string, and into the address of the page.
export type OfferFilters = {
  title: string;
  city: string;
  country: string;
  contract: Contract | "";
  remote: Remote | "";
  salary_min: string;
  salary_period: SalaryPeriod;
  currency: Currency;
  published_after: string;
};

export const EMPTY_FILTERS: OfferFilters = {
  title: "",
  city: "",
  country: "",
  contract: "",
  remote: "",
  salary_min: "",
  salary_period: "month",
  currency: "CHF",
  published_after: "",
};

// What an employer writes in an offer: the fields of the form, the numbers
// as numbers, or null for an empty field. The status is not here: it moves
// through publishOffer and closeOffer.
export type OfferInput = {
  title: string;
  description: string;
  city: string;
  country: string;
  remote: Remote;
  contract: Contract | "";
  workload_min: number | null;
  workload_max: number | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_period: SalaryPeriod;
  currency: Currency;
  experience_years: number | null;
};

export const EMPTY_INPUT: OfferInput = {
  title: "",
  description: "",
  city: "",
  country: "",
  remote: "on_site",
  contract: "",
  workload_min: null,
  workload_max: null,
  salary_min: null,
  salary_max: null,
  salary_period: "month",
  currency: "CHF",
  experience_years: null,
};

// The fields of an offer an employer may write, as the form shows them
export function inputOf(offer: Offer): OfferInput {
  const input: Partial<OfferInput> = {};
  for (const key of Object.keys(EMPTY_INPUT) as (keyof OfferInput)[]) {
    input[key] = offer[key] as never;
  }
  return input as OfferInput;
}

// ── Reading ───────────────────────────────────────────────────────────

// The published offers, newest first, filtered and paged (PAGE_SIZE by page)
export function listOffers(filters: OfferFilters, page: number): Promise<OfferPage> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    // The period and the currency only qualify an amount: alone, they say nothing
    const qualifies = key === "salary_period" || key === "currency";
    if (value && (!qualifies || filters.salary_min)) params.set(key, value);
  }
  if (page > 1) params.set("page", String(page));
  const query = params.toString();
  return getJson<OfferPage>("/api/offers/" + (query ? "?" + query : ""));
}

// One offer: published, or the employer's own; 404 otherwise
export function getOffer(id: number): Promise<Offer> {
  return getJson<Offer>(`/api/offers/${id}/`);
}

// ── The management, for an employer ───────────────────────────────────
// Every call answers with its status: a 400 carries the errors by field
// (or under non_field_errors for a refused move), a 403 means the account
// is not an employer, a 404 that the offer is somebody else's

// The first message of a refused request, whatever its field: a refused
// move (publish, close) has one reason, under non_field_errors
export function firstErrorOf(data: unknown): string {
  return Object.values(firstErrors(data as Record<string, string[]> | null))[0] ?? "";
}

// All the offers of the employer, in any state, newest first
export function myOffers(): Promise<Offer[]> {
  return getJson<Offer[]>("/api/offers/mine/");
}

// A new offer, born as a draft
export function createOffer(input: OfferInput): Promise<Answer<Offer>> {
  return send<Offer>("POST", "/api/offers/", input);
}

// The fields sent replace the stored ones; the status does not move
export function updateOffer(id: number, input: OfferInput): Promise<Answer<Offer>> {
  return send<Offer>("PATCH", `/api/offers/${id}/`, input);
}

export function deleteOffer(id: number): Promise<Answer<null>> {
  return send<null>("DELETE", `/api/offers/${id}/`);
}

// Draft or closed -> published; refused when the company has no name
export function publishOffer(id: number): Promise<Answer<Offer>> {
  return send<Offer>("POST", `/api/offers/${id}/publish/`);
}

// Published -> closed: out of the public list, kept by the employer
export function closeOffer(id: number): Promise<Answer<Offer>> {
  return send<Offer>("POST", `/api/offers/${id}/close/`);
}
