<!--
  frontend/src/pages/ApplyPage.vue

  Apply page — a candidate applies to one offer
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/offers/<id>/apply", to a candidate only (the
  router sends anyone else away). The offer and the profile are read first:
  the CV of the profile is offered as the default, a file otherwise; a cover
  letter may be joined, and the documents of the profile are ticked to be
  joined as copies. One request sends everything; once accepted, the page
  of the offer shows the application sent. An offer already applied to, or
  not open, is said so with a way out.
-->

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute, useRouter } from "vue-router";

import { apply, listApplications } from "../api/applications";
import { firstErrors } from "../api/http";
import { getOffer, type Offer } from "../api/offers";
import { ACCEPTED, MAX_FILE_SIZE, fileProblem, getProfile, type CandidateProfile } from "../api/profile";

const { t } = useI18n();
const route = useRoute();
const router = useRouter();

const offerId = Number(route.params.id);
const offer = ref<Offer | null>(null);
const profile = ref<CandidateProfile | null>(null);
// What stops the form: the offer is not open, or already applied to
const notOpen = ref(false);
const alreadyApplied = ref(false);
const loadFailed = ref(false);

// What the candidate chooses
const useProfileCv = ref(false);
const cv = ref<File | null>(null);
const coverLetter = ref<File | null>(null);
const documents = ref<number[]>([]);

const errors = ref<Record<string, string>>({});
const sending = ref(false);

// The name of the CV of the profile, read from its URL
const profileCvName = computed(() => {
  const url = profile.value?.cv;
  return url ? decodeURIComponent(url.split("/").pop() ?? "") : "";
});

// The rules, as the texts show them: "PDF, DOCX" and 5
function types(kind: "cv" | "document"): string {
  return ACCEPTED[kind].map((extension) => extension.slice(1).toUpperCase()).join(", ");
}
const sizeInMb = MAX_FILE_SIZE / (1024 * 1024);

async function load(): Promise<void> {
  try {
    const [found, mine, me] = await Promise.all([
      getOffer(offerId).catch(() => null),
      listApplications({ offer: offerId }),
      getProfile<CandidateProfile>(),
    ]);
    offer.value = found;
    profile.value = me;
    notOpen.value = !found || found.status !== "published";
    alreadyApplied.value = mine.length > 0;
    useProfileCv.value = Boolean(me.cv);
  } catch {
    loadFailed.value = true;
  }
}

// The file chosen in an input, checked against the rules: kept for the
// field, or refused with the reason under it. The input forgets the choice,
// so that choosing the same file again fires again
function chosen(event: Event, field: "cv" | "coverLetter"): void {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0] ?? null;
  input.value = "";
  delete errors.value[field];
  if (!file) return;
  const problem = fileProblem(file, "cv");
  if (problem) {
    errors.value[field] = t(`apply.${problem}`, { size: sizeInMb, types: types("cv") });
    return;
  }
  if (field === "cv") cv.value = file;
  else coverLetter.value = file;
}

async function submit(): Promise<void> {
  errors.value = {};
  if (!useProfileCv.value && !cv.value) {
    errors.value.cv = t("apply.cvRequired");
    return;
  }
  sending.value = true;
  try {
    const answer = await apply({
      offer: offerId,
      cv: cv.value,
      useProfileCv: useProfileCv.value,
      coverLetter: coverLetter.value,
      documents: documents.value,
    });
    if (answer.status === 201) {
      router.replace({ name: "offer", params: { id: offerId } });
    } else if (answer.status === 400) {
      // The errors by field; the letter is "cover_letter" for the backend
      const byField = firstErrors(answer.data as unknown as Record<string, string[]>);
      errors.value = byField;
      if (byField.cover_letter) errors.value.coverLetter = byField.cover_letter;
    } else {
      errors.value = { "": t("form.failed") };
    }
  } catch {
    errors.value = { "": t("form.unreachable") };
  } finally {
    sending.value = false;
  }
}

onMounted(load);
</script>

<template>
  <p class="back">
    <RouterLink :to="{ name: 'offer', params: { id: offerId } }">← {{ t("apply.back") }}</RouterLink>
  </p>

  <h1>{{ t("apply.title") }}</h1>

  <p v-if="loadFailed" class="error">{{ t("form.unreachable") }}</p>

  <template v-else-if="offer !== null || notOpen">
    <p v-if="offer" class="offer">
      <strong>{{ offer.title }}</strong> · {{ offer.company.name }}, {{ offer.city }}
    </p>

    <p v-if="notOpen" class="notice">{{ t("apply.notOpen") }}</p>

    <p v-else-if="alreadyApplied" class="notice">
      {{ t("apply.alreadyApplied") }}
      <RouterLink :to="{ name: 'myApplications' }">{{ t("apply.myApplicationsLink") }}</RouterLink>
    </p>

    <!-- novalidate: the page and the backend check the fields themselves -->
    <form v-else-if="profile" novalidate @submit.prevent="submit">
      <p v-if="errors['']" class="error">{{ errors[""] }}</p>

      <!-- The CV: the one of the profile, or a file -->
      <fieldset class="field choices">
        <legend>{{ t("apply.cv") }}</legend>
        <template v-if="profile.cv">
          <label class="choice">
            <input v-model="useProfileCv" type="radio" :value="true" />
            {{ t("apply.cvProfile", { name: profileCvName }) }}
          </label>
          <label class="choice">
            <input v-model="useProfileCv" type="radio" :value="false" />
            {{ t("apply.cvOther") }}
          </label>
        </template>
        <p v-else class="hint">{{ t("apply.cvNone") }}</p>
        <!-- A label styled as a button opens the file dialog of its hidden
             input; the file chosen is named next to it -->
        <p v-if="!useProfileCv" class="file-actions">
          <label class="secondary">
            {{ cv ? t("apply.replace") : t("apply.choose") }}
            <input type="file" :accept="ACCEPTED.cv.join(',')" hidden @change="chosen($event, 'cv')" />
          </label>
          <span v-if="cv">{{ cv.name }}</span>
          <button v-if="cv" type="button" class="as-link" @click="cv = null">{{ t("apply.remove") }}</button>
          <span v-else class="hint">{{ t("apply.fileHint", { types: types("cv"), size: sizeInMb }) }}</span>
        </p>
        <p v-if="errors.cv" class="error">{{ errors.cv }}</p>
      </fieldset>

      <!-- The cover letter, optional -->
      <fieldset class="field choices">
        <legend>{{ t("apply.coverLetter") }}</legend>
        <p class="file-actions">
          <label class="secondary">
            {{ coverLetter ? t("apply.replace") : t("apply.choose") }}
            <input type="file" :accept="ACCEPTED.cv.join(',')" hidden @change="chosen($event, 'coverLetter')" />
          </label>
          <span v-if="coverLetter">{{ coverLetter.name }}</span>
          <button v-if="coverLetter" type="button" class="as-link" @click="coverLetter = null">{{ t("apply.remove") }}</button>
          <span v-else class="hint">{{ t("apply.fileHint", { types: types("cv"), size: sizeInMb }) }}</span>
        </p>
        <p v-if="errors.coverLetter" class="error">{{ errors.coverLetter }}</p>
      </fieldset>

      <!-- The documents of the profile, ticked to be joined -->
      <fieldset class="field choices">
        <legend>{{ t("apply.documents") }}</legend>
        <template v-if="profile.documents.length">
          <label v-for="document in profile.documents" :key="document.id" class="choice">
            <input v-model="documents" type="checkbox" :value="document.id" />
            {{ document.name }}
          </label>
        </template>
        <p v-else class="hint">
          {{ t("apply.documentsNone") }}
          <RouterLink :to="{ name: 'profile' }">{{ t("apply.profileLink") }}</RouterLink>
        </p>
        <p v-if="errors.documents" class="error">{{ errors.documents }}</p>
      </fieldset>

      <button type="submit" class="primary" :disabled="sending">{{ t("apply.submit") }}</button>
    </form>
  </template>
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

/* The offer applied to, under the title */
.offer {
  margin: -8px 0 20px;
  color: var(--mt-muted);
}

.offer strong {
  color: var(--mt-text);
}

.notice a {
  margin-left: 6px;
}

/* The legends flush with the title, the choices one per line, unlike the
   side-by-side choices of the forms */
.choices legend {
  padding: 0;
}

.choice {
  display: block;
  margin: 0 0 6px;
  font-weight: normal;
}

.choice input {
  margin-right: 8px;
}

/* The button of a file, the name chosen and the way to forget it, side
   by side */
.file-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin: 4px 0 0;
}

.secondary {
  display: inline-block;
  padding: 8px 16px;
  border: 1px solid var(--mt-border);
  border-radius: 4px;
  background: var(--mt-surface);
  color: var(--mt-text);
  font: inherit;
  font-weight: normal;
  cursor: pointer;
}

.secondary:hover {
  background: var(--mt-border);
}

.hint {
  margin: 4px 0 0;
  color: var(--mt-muted);
  font-size: 0.9rem;
}

.file-actions .hint {
  margin: 0;
}

.hint a {
  margin-left: 4px;
}
</style>
