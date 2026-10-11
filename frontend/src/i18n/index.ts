// frontend/src/i18n/index.ts
//
// Internationalisation — languages of the interface
// ─────────────────────────────────────────────────────────────────────────────
// Creates the translation engine, chooses the language shown on the first
// visit and remembers the language chosen by the user.

import { createI18n } from "vue-i18n";

import en from "./locales/en";
import fr from "./locales/fr";

// Languages offered by the selector. Each name is written in its own language
// so that anyone can find theirs, whatever language is currently displayed.
export const LOCALES = [
  { code: "en", name: "English" },
  { code: "fr", name: "Français" },
] as const;

// "en" | "fr", derived from the list above
export type Locale = (typeof LOCALES)[number]["code"];

// Used when the browser language is not one of ours
const DEFAULT_LOCALE: Locale = "en";

// Name under which the browser stores the user's choice
const STORAGE_KEY = "marketech.locale";

// Tells whether a text coming from outside is one of our language codes
function isLocale(value: string | null): value is Locale {
  return LOCALES.some((locale) => locale.code === value);
}

// Language shown at start-up: the stored choice, otherwise the browser
// language, otherwise the default one
function initialLocale(): Locale {
  const stored = localStorage.getItem(STORAGE_KEY);
  if (isLocale(stored)) return stored;

  // "fr-CH" becomes "fr"
  const browser = navigator.language.split("-")[0];
  return isLocale(browser) ? browser : DEFAULT_LOCALE;
}

export const i18n = createI18n({
  // Composition API mode, the one used by <script setup> components
  legacy: false,
  locale: initialLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: { en, fr },
});

// Changes the language, remembers the choice and tells the browser which
// language the page is written in
export function setLocale(locale: Locale): void {
  i18n.global.locale.value = locale;
  localStorage.setItem(STORAGE_KEY, locale);
  document.documentElement.lang = locale;
}

// The page starts in the language chosen above
document.documentElement.lang = i18n.global.locale.value;
