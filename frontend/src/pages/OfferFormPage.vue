<!--
  frontend/src/pages/OfferFormPage.vue

  Offer form page — a new offer, or one to change
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/employer/offers/new" and for
  "/employer/offers/<id>/edit", to an employer only. One form for both: with
  a number in the address, the offer is loaded into it, else the form starts
  empty. Two buttons, two outcomes: "Save" keeps the state of the offer (a
  new one is a draft); "Save and publish" saves, then publishes, for a draft
  or a closed offer. The errors of the backend show under their field; a
  refused publication shows at the top, with a link to the profile when the
  company has no name yet.
-->

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import {
  CONTRACTS,
  CURRENCIES,
  EMPTY_INPUT,
  REMOTES,
  SALARY_PERIODS,
  createOffer,
  firstErrorOf,
  getOffer,
  inputOf,
  isCompanyMissing,
  publishOffer,
  updateOffer,
  type Offer,
  type OfferInput,
} from "../api/offers";
import { firstErrors } from "../api/http";
import { getCountries, type Country } from "../api/profile";

const { t, locale } = useI18n();
const route = useRoute();
const router = useRouter();

// The number in the address, or null for a new offer
const id = computed(() => (route.params.id ? Number(route.params.id) : null));
// The offer being changed, once loaded; stays null for a new one
const offer = ref<Offer | null>(null);
const notFound = ref(false);

const input = reactive<OfferInput>({ ...EMPTY_INPUT });
const countries = ref<Country[]>([]);

// What the page shows about the form: errors by field ("" for the whole
// form), a save in flight, and a link to the profile when the publication
// was refused for want of a company name
const errors = ref<Record<string, string>>({});
const saving = ref(false);
const needsCompany = ref(false);

// A draft or a closed offer can be published from here; a published one
// is just saved
const canPublish = computed(() => !offer.value || offer.value.status !== "published");

// The fields an offer cannot do without, checked here first for a clear
// message in the language of the page; the backend checks them again
const REQUIRED = ["title", "description", "city", "country", "contract"] as const;

// The numbers of the form: a field left empty holds "", sent as null
const NUMBERS = ["workload_min", "workload_max", "salary_min", "salary_max", "experience_years"] as const;

function payload(): OfferInput {
  const data = { ...input };
  for (const key of NUMBERS) {
    if ((data[key] as unknown) === "") data[key] = null;
  }
  return data;
}

async function load(): Promise<void> {
  notFound.value = false;
  if (id.value === null) {
    offer.value = null;
    Object.assign(input, EMPTY_INPUT);
    return;
  }
  try {
    offer.value = await getOffer(id.value);
    Object.assign(input, inputOf(offer.value));
  } catch {
    // 404: not an offer of this employer, or no such offer
    notFound.value = true;
  }
}

async function loadCountries(): Promise<void> {
  try {
    countries.value = await getCountries();
  } catch {
    // The list stays empty: the field shows its codes
  }
}

// Saves, then publishes when asked; goes back to the list when all went
// well. A new offer saved but not published (the publication refused)
// stays on this page, under its own address, so that saving again changes
// it instead of creating a second one.
async function submit(publish: boolean): Promise<void> {
  errors.value = {};
  needsCompany.value = false;
  const missing = REQUIRED.filter((key) => !input[key]);
  if (missing.length) {
    errors.value = Object.fromEntries(missing.map((key) => [key, t("offerForm.required")]));
    return;
  }
  saving.value = true;
  try {
    const answer = offer.value ? await updateOffer(offer.value.id, payload()) : await createOffer(payload());
    if (!answer.data || (answer.status !== 200 && answer.status !== 201)) {
      errors.value = firstErrors(answer.data as Record<string, string[]> | null);
      if (!Object.keys(errors.value).length) errors.value = { "": t("form.failed") };
      return;
    }
    const saved = answer.data;
    if (!offer.value) {
      offer.value = saved;
      await router.replace({ name: "offerEdit", params: { id: saved.id } });
    }
    if (publish) {
      const published = await publishOffer(saved.id);
      if (published.status !== 200) {
        // Saved, not published: the reason as the backend words it, in the
        // language of the page; a company without a name links to the profile
        needsCompany.value = isCompanyMissing(published.data);
        errors.value = { "": firstErrorOf(published.data) || t("form.failed") };
        return;
      }
    }
    await router.push({ name: "myOffers" });
  } catch {
    errors.value = { "": t("form.unreachable") };
  } finally {
    saving.value = false;
  }
}

watch(locale, loadCountries);
watch(id, load);

onMounted(() => {
  load();
  loadCountries();
});
</script>

<template>
  <p class="back">
    <RouterLink :to="{ name: 'myOffers' }">← {{ t("offerForm.back") }}</RouterLink>
  </p>

  <div class="head">
    <h1>{{ offer ? t("offerForm.editTitle") : t("offerForm.newTitle") }}</h1>
    <!-- The applications received by the offer being edited -->
    <RouterLink
      v-if="offer && offer.status !== 'draft'"
      :to="{ name: 'receivedApplications', query: { offer: String(offer.id) } }"
      class="secondary applications"
    >
      {{ t("myOffers.applications", offer.applications_count ?? 0) }}
    </RouterLink>
  </div>

  <p v-if="notFound" class="notice">{{ t("offerForm.notFound") }}</p>

  <form v-else class="form" novalidate @submit.prevent="submit(false)">
    <p v-if="errors['']" class="error top">
      {{ errors[""] }}
      <RouterLink v-if="needsCompany" :to="{ name: 'profile' }">{{ t("myOffers.companyLink") }}</RouterLink>
    </p>

    <div class="fields">
      <div class="field wide">
        <label for="title">{{ t("offerForm.title") }}</label>
        <input id="title" v-model.trim="input.title" type="text" maxlength="200" />
        <p v-if="errors.title" class="error">{{ errors.title }}</p>
      </div>
      <div class="field wide">
        <label for="description">{{ t("offerForm.description") }}</label>
        <textarea id="description" v-model="input.description" rows="10"></textarea>
        <p class="muted hint">{{ t("offerForm.descriptionHint") }}</p>
        <p v-if="errors.description" class="error">{{ errors.description }}</p>
      </div>
      <div class="field">
        <label for="city">{{ t("offerForm.city") }}</label>
        <input id="city" v-model.trim="input.city" type="text" maxlength="100" />
        <p v-if="errors.city" class="error">{{ errors.city }}</p>
      </div>
      <div class="field">
        <label for="country">{{ t("offerForm.country") }}</label>
        <select id="country" v-model="input.country">
          <option value="">{{ t("offerForm.chooseCountry") }}</option>
          <option v-for="(country, index) in countries" :key="index" :value="country.code">
            {{ country.name }}
          </option>
        </select>
        <p v-if="errors.country" class="error">{{ errors.country }}</p>
      </div>
      <div class="field">
        <label for="contract">{{ t("offerForm.contract") }}</label>
        <select id="contract" v-model="input.contract">
          <option value="">{{ t("offerForm.chooseContract") }}</option>
          <option v-for="contract in CONTRACTS" :key="contract" :value="contract">
            {{ t("offers.contract." + contract) }}
          </option>
        </select>
        <p v-if="errors.contract" class="error">{{ errors.contract }}</p>
      </div>
      <div class="field">
        <label for="remote">{{ t("offerForm.remote") }}</label>
        <select id="remote" v-model="input.remote">
          <option v-for="remote in REMOTES" :key="remote" :value="remote">
            {{ t("offers.remote." + remote) }}
          </option>
        </select>
        <p v-if="errors.remote" class="error">{{ errors.remote }}</p>
      </div>
      <div class="field">
        <label for="workload_min">{{ t("offerForm.workload") }}</label>
        <div class="pair">
          <input id="workload_min" v-model.number="input.workload_min" type="number" min="10" max="100" step="10" />
          <span class="dash">–</span>
          <input v-model.number="input.workload_max" type="number" min="10" max="100" step="10" :aria-label="t('offerForm.workloadMax')" />
        </div>
        <p class="muted hint">{{ t("offerForm.workloadHint") }}</p>
        <p v-if="errors.workload_min || errors.workload_max" class="error">
          {{ errors.workload_min || errors.workload_max }}
        </p>
      </div>
      <div class="field">
        <label for="experience_years">{{ t("offerForm.experience") }}</label>
        <input id="experience_years" v-model.number="input.experience_years" type="number" min="0" max="50" />
        <p v-if="errors.experience_years" class="error">{{ errors.experience_years }}</p>
      </div>
      <div class="field wide">
        <label for="salary_min">{{ t("offerForm.salary") }}</label>
        <div class="pair">
          <input id="salary_min" v-model.number="input.salary_min" type="number" min="0" step="100" />
          <span class="dash">–</span>
          <input v-model.number="input.salary_max" type="number" min="0" step="100" :aria-label="t('offerForm.salaryMax')" />
          <select v-model="input.currency" :aria-label="t('offers.currencyLabel')">
            <option v-for="currency in CURRENCIES" :key="currency" :value="currency">{{ currency }}</option>
          </select>
          <select v-model="input.salary_period" :aria-label="t('offers.periodLabel')">
            <option v-for="period in SALARY_PERIODS" :key="period" :value="period">
              {{ t("offers.period." + period) }}
            </option>
          </select>
        </div>
        <p class="muted hint">{{ t("offerForm.salaryHint") }}</p>
        <p v-if="errors.salary_min || errors.salary_max" class="error">
          {{ errors.salary_min || errors.salary_max }}
        </p>
      </div>
    </div>

    <p class="actions">
      <button v-if="canPublish" type="button" class="primary" :disabled="saving" @click="submit(true)">
        {{ offer?.status === "closed" ? t("offerForm.saveAndRepublish") : t("offerForm.saveAndPublish") }}
      </button>
      <button type="submit" :class="canPublish ? 'secondary' : 'primary'" :disabled="saving">
        {{ t("offerForm.save") }}
      </button>
    </p>
  </form>
</template>

<style scoped>
.back {
  margin: 0 0 16px;
}

.back a {
  text-decoration: none;
}

.back a:hover {
  text-decoration: underline;
}

/* The title on the left, the link to the applications on the right */
.head {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.applications {
  text-decoration: none;
}

h1 {
  margin-top: 0;
}

/* The fields on two columns; a wide field takes the row */
.fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 24px;
  max-width: 900px;
}

.fields .wide {
  grid-column: 1 / -1;
}

.fields .field input,
.fields .field select,
.fields .field textarea {
  max-width: none;
}

.field textarea {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-background);
  color: var(--mt-text);
  font: inherit;
  resize: vertical;
}

/* Two amounts and their units, side by side */
.pair {
  display: flex;
  align-items: center;
  gap: 8px;
}

.pair input {
  flex: 1;
  min-width: 0;
}

.pair select {
  width: auto;
}

.dash {
  color: var(--mt-muted);
}

.muted {
  color: var(--mt-muted);
}

.hint {
  margin: 4px 0 0;
  font-size: 0.85rem;
}

.top {
  margin: 0 0 16px;
}

.top a {
  margin-left: 6px;
}

.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 8px 0 0;
}

.secondary {
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  cursor: pointer;
}

.secondary:hover {
  background: var(--mt-border);
}

.secondary:disabled {
  opacity: 0.6;
  cursor: default;
}

@media (max-width: 720px) {
  .fields {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
