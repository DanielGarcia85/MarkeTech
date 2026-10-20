// frontend/src/api/offers.ts
//
// Offers API — the job offers, as the backend serves them
// ─────────────────────────────────────────────────────────────────────────────
// The types of an offer and of a page of offers, the filters of the public
// list, and one function per route of reading. The choices (contract,
// remote work, salary period, status) are the values stored by the backend;
// their texts are in the language files, under offers.*.

import { getJson } from "./http";

// ── Types ─────────────────────────────────────────────────────────────

export type Contract = "permanent" | "fixed_term" | "internship" | "student";
export type Remote = "on_site" | "hybrid" | "remote";
export type SalaryPeriod = "month" | "year";
export type OfferStatus = "draft" | "published" | "closed";

// The lists of the choices, in the order the forms and the filters show them
export const CONTRACTS: Contract[] = ["permanent", "fixed_term", "internship", "student"];
export const REMOTES: Remote[] = ["on_site", "hybrid", "remote"];
export const SALARY_PERIODS: SalaryPeriod[] = ["month", "year"];

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
  published_after: "",
};

// ── Reading ───────────────────────────────────────────────────────────

// The published offers, newest first, filtered and paged (PAGE_SIZE by page)
export function listOffers(filters: OfferFilters, page: number): Promise<OfferPage> {
  const params = new URLSearchParams();
  for (const [key, value] of Object.entries(filters)) {
    // The period only qualifies an amount: alone, it says nothing
    if (value && (key !== "salary_period" || filters.salary_min)) params.set(key, value);
  }
  if (page > 1) params.set("page", String(page));
  const query = params.toString();
  return getJson<OfferPage>("/api/offers/" + (query ? "?" + query : ""));
}

// One offer: published, or the employer's own; 404 otherwise
export function getOffer(id: number): Promise<Offer> {
  return getJson<Offer>(`/api/offers/${id}/`);
}
