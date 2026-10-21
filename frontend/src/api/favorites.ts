// frontend/src/api/favorites.ts
//
// Favorites API — the offers a candidate puts aside, as the backend serves them
// ─────────────────────────────────────────────────────────────────────────────
// The type of a favorite and one function per route: the list of one's
// favorites, putting an offer aside, taking it back. Whether an offer is a
// favorite of the logged-in candidate comes with the offer itself (the
// "favorite" flag of api/offers.ts): the heart reads it, these calls change
// it.

import { getJson, send, type Answer } from "./http";
import type { Offer } from "./offers";

// A favorite as the API gives it: the offer as the cards show it (its
// "favorite" flag true), and when it was put aside
export type Favorite = {
  id: number;
  offer: Offer;
  created_at: string;
};

// One's favorites, newest first
export function listFavorites(): Promise<Favorite[]> {
  return getJson<Favorite[]>("/api/favorites/");
}

// Put a published offer aside; 400 when it already is, or cannot be
export function addFavorite(offerId: number): Promise<Answer<Favorite>> {
  return send<Favorite>("POST", "/api/favorites/", { offer: offerId });
}

// Take an offer back, by the offer: 404 when it is not among one's favorites
export function removeFavorite(offerId: number): Promise<Answer<null>> {
  return send<null>("DELETE", `/api/favorites/${offerId}/`);
}
