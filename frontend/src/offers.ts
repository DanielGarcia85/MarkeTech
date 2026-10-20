// frontend/src/offers.ts
//
// Offer texts — how an offer is written on the pages
// ─────────────────────────────────────────────────────────────────────────────
// The lines that the list and the detail page share: the place, the
// conditions, the salary, the date. A composable, because the words and the
// number formats depend on the language displayed.

import { useI18n } from "vue-i18n";

import type { Country } from "./api/profile";
import type { Offer } from "./api/offers";

export function useOfferText() {
  const { t, locale } = useI18n();

  // "Geneva, Switzerland": the name of the country comes from the list of
  // the countries route, by its code; the code itself until the list is here
  function place(offer: Offer, countries: Country[]): string {
    const country = countries.find((c) => c.code === offer.country)?.name ?? offer.country;
    return `${offer.city}, ${country}`;
  }

  // "Permanent · 80–100 % · Hybrid": the contract, the workload when given,
  // the remote work
  function conditions(offer: Offer): string {
    const parts = [t("offers.contract." + offer.contract)];
    if (offer.workload_min || offer.workload_max) {
      const low = offer.workload_min ?? offer.workload_max;
      const high = offer.workload_max ?? offer.workload_min;
      parts.push(low === high ? `${low} %` : `${low}–${high} %`);
    }
    parts.push(t("offers.remote." + offer.remote));
    return parts.join(" · ");
  }

  // "CHF 6 000 – 8 000 per month", "from CHF 90 000 per year", "up to ...",
  // or "" when the offer says nothing about the salary
  function salary(offer: Offer): string {
    const amount = new Intl.NumberFormat(locale.value, { maximumFractionDigits: 0 });
    const { salary_min: low, salary_max: high } = offer;
    const period = t("offers.period." + offer.salary_period);
    if (low && high) {
      const range = low === high ? amount.format(low) : `${amount.format(low)} – ${amount.format(high)}`;
      return t("offers.salary.range", { range, period });
    }
    if (low) return t("offers.salary.from", { amount: amount.format(low), period });
    if (high) return t("offers.salary.upTo", { amount: amount.format(high), period });
    return "";
  }

  // "3 years of experience" or "" when not asked; the count picks the
  // singular or the plural of the text
  function experience(offer: Offer): string {
    return offer.experience_years ? t("offers.experience", offer.experience_years) : "";
  }

  // The date of publication, as "20 October 2026" in the language displayed
  function published(offer: Offer): string {
    if (!offer.published_at) return "";
    return new Intl.DateTimeFormat(locale.value, { dateStyle: "long" }).format(new Date(offer.published_at));
  }

  return { place, conditions, salary, experience, published };
}
