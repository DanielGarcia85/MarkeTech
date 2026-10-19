<!--
  frontend/src/pages/ProfilePage.vue

  Profile page — the names, contact details, company, files and account
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/profile", for a logged-in user only: the router
  sends a visitor to the login page. The page depends on the role: a
  candidate has a photo, a CV and further documents; an employer has a
  company and a logo. Laid out in sections separated by a rule, the fields
  on two columns on a wide window, one on a narrow one. The text fields,
  names included, are saved together by the Save button; a file is sent as
  soon as it is chosen, and removed after a confirmation. The account comes
  last: a new e-mail address, confirmed by a link sent to it, and a new
  password, given with the current one. Every action done shows a short
  confirmation next to where it happened.
-->

<script setup lang="ts">
import { computed, reactive, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import {
  cancelEmailChange,
  changeEmail,
  changePassword,
  listEmails,
  type EmailAddressInfo,
} from "../api/account";
import { errorsByParam, firstErrors } from "../api/http";
import {
  ACCEPTED,
  MAX_DOCUMENTS,
  MAX_FILE_SIZE,
  addDocument,
  fileProblem,
  getCountries,
  getProfile,
  removeDocument,
  removeFile,
  updateProfile,
  uploadFile,
  type CandidateProfile,
  type Country,
  type EmployerProfile,
  type Profile,
  type ProfileFields,
  type ProfileFileField,
} from "../api/profile";
import { loadSession, useSession } from "../session";

const { t, locale } = useI18n();
const session = useSession();

// ── The confirmations ─────────────────────────────────────────────────

// The kinds of file of the page: the three fields of the profile, and the
// further documents of a candidate
type FileKind = ProfileFileField | "document";

// Where a confirmation can appear: next to the Save button, in each file
// block, under the password form
type BadgePlace = "form" | FileKind | "password";

// The confirmation shown at each place, if any: its text, and a number
// that changes at every showing, so that the animation starts again when
// the same place is confirmed twice in a row
const badges = reactive<Partial<Record<BadgePlace, { text: string; id: number }>>>({});
const BADGE_DURATION = 3000;
let badgeId = 0;
const badgeTimers: Partial<Record<BadgePlace, number>> = {};

function showBadge(place: BadgePlace, text: string): void {
  badges[place] = { text, id: ++badgeId };
  // A confirmation replaces the previous one of the same place, and leaves
  // after its time
  window.clearTimeout(badgeTimers[place]);
  badgeTimers[place] = window.setTimeout(() => {
    delete badges[place];
  }, BADGE_DURATION);
}

// ── The profile ───────────────────────────────────────────────────────

// The profile as the backend gave it last; null until loaded
const profile = ref<Profile | null>(null);
const loadFailed = ref(false);

// The same profile, typed by role, for the template
const candidate = computed(() =>
  session.user?.role === "candidate" ? (profile.value as CandidateProfile) : null,
);
const employer = computed(() =>
  session.user?.role === "employer" ? (profile.value as EmployerProfile) : null,
);

// The text fields being edited, filled from the profile once loaded
const fields = reactive<ProfileFields>({});

// The letters shown in place of a missing photo: the initials of the name
// as the header shows them
const initials = computed(() => {
  const words = (session.user?.display ?? "").split(/\s+/).filter((word) => word.length > 0);
  const first = words[0] ?? "";
  const last = words.length > 1 ? (words[words.length - 1] ?? "") : "";
  return (last ? first.charAt(0) + last.charAt(0) : first.slice(0, 2)).toUpperCase();
});

// One entry per field of the form: its name in the API, its label, the
// hint the browser uses to fill it in, whether it takes a whole row, and
// whether it is a country, chosen in a list rather than typed
type FieldDefinition = {
  key: keyof ProfileFields;
  label: string;
  autocomplete: string;
  wide?: boolean;
  country?: boolean;
};
const IDENTITY_FIELDS: FieldDefinition[] = [
  { key: "first_name", label: "profile.firstName", autocomplete: "given-name" },
  { key: "last_name", label: "profile.lastName", autocomplete: "family-name" },
];
const CONTACT_FIELDS: FieldDefinition[] = [
  { key: "phone", label: "profile.phone", autocomplete: "tel" },
  { key: "address", label: "profile.address", autocomplete: "street-address", wide: true },
  { key: "postal_code", label: "profile.postalCode", autocomplete: "postal-code" },
  { key: "city", label: "profile.city", autocomplete: "address-level2" },
  { key: "country", label: "profile.country", autocomplete: "country", country: true },
];
const COMPANY_FIELDS: FieldDefinition[] = [
  { key: "company_name", label: "profile.companyName", autocomplete: "organization" },
  { key: "company_address", label: "profile.companyAddress", autocomplete: "off", wide: true },
  { key: "company_postal_code", label: "profile.companyPostalCode", autocomplete: "off" },
  { key: "company_city", label: "profile.companyCity", autocomplete: "off" },
  { key: "company_country", label: "profile.companyCountry", autocomplete: "off", country: true },
  { key: "company_phone", label: "profile.companyPhone", autocomplete: "off" },
];

// What the page shows about the form: errors by field, a save in flight
const errors = ref<Record<string, string>>({});
const saving = ref(false);

// The countries offered by the lists, in the language of the interface:
// read with the profile, and again when the language changes
const countries = ref<Country[]>([]);

async function loadCountries(): Promise<void> {
  try {
    countries.value = await getCountries();
  } catch {
    // The lists stay empty; the chosen code is kept and saved as it is
  }
}

watch(locale, loadCountries);

async function load(): Promise<void> {
  try {
    profile.value = await getProfile();
    // Copy every text field of the profile into the form
    for (const definition of [...IDENTITY_FIELDS, ...CONTACT_FIELDS, ...COMPANY_FIELDS]) {
      const value = (profile.value as Record<string, unknown>)[definition.key];
      if (typeof value === "string") fields[definition.key] = value;
    }
  } catch {
    loadFailed.value = true;
    return;
  }
  loadCountries();
  loadEmails();
}

// Runs once, when the page opens: the router has already made sure that
// someone is logged in
load();

async function save(): Promise<void> {
  errors.value = {};
  saving.value = true;
  // The header shows the name of the account: reloaded below if it changes
  const namesChanged =
    fields.first_name !== profile.value?.first_name ||
    fields.last_name !== profile.value?.last_name;
  try {
    const answer = await updateProfile<Profile>(fields);
    if (answer.status === 200 && answer.data) {
      profile.value = answer.data;
      showBadge("form", t("profile.saved"));
      if (namesChanged) await loadSession();
    } else {
      errors.value = firstErrors(answer.data as Record<string, string[]> | null);
      if (!Object.keys(errors.value).length) errors.value = { "": t("form.failed") };
    }
  } catch {
    errors.value = { "": t("form.unreachable") };
  } finally {
    saving.value = false;
  }
}

// ── The files ─────────────────────────────────────────────────────────

// Which kind is being sent, and the last error of each kind
const sending = ref<FileKind | null>(null);
const fileErrors = ref<Partial<Record<FileKind, string>>>({});

// The rules, as the texts show them: "PNG, JPG, JPEG" and 5
function types(kind: FileKind): string {
  return ACCEPTED[kind].map((extension) => extension.slice(1).toUpperCase()).join(", ");
}
const sizeInMb = MAX_FILE_SIZE / (1024 * 1024);

// The name of a file, read from its URL
function fileName(url: string): string {
  return decodeURIComponent(url.split("/").pop() ?? "");
}

// The file chosen in an input, checked against the rules; null when there
// is none or it breaks a rule (the error is shown under the field)
function chosenFile(event: Event, kind: FileKind): File | null {
  const input = event.target as HTMLInputElement;
  const file = input.files?.[0] ?? null;
  // Forget the choice, so that choosing the same file again fires again
  input.value = "";
  if (!file) return null;
  const problem = fileProblem(file, kind);
  if (problem) {
    fileErrors.value[kind] = t(`profile.${problem}`, { size: sizeInMb, types: types(kind) });
    return null;
  }
  return file;
}

// Error of a file call: the message of the backend for that field, or a
// general one
function fileError(kind: FileKind, data: unknown): string {
  const byField = firstErrors(data as Record<string, string[]> | null);
  return byField[kind === "document" ? "file" : kind] ?? byField[""] ?? t("form.failed");
}

// Sends a file of the profile (photo, CV, logo) as soon as it is chosen
async function sendFile(event: Event, kind: ProfileFileField): Promise<void> {
  fileErrors.value[kind] = undefined;
  const file = chosenFile(event, kind);
  if (!file) return;
  sending.value = kind;
  try {
    const answer = await uploadFile<Profile>(kind, file);
    if (answer.status === 200 && answer.data) {
      profile.value = answer.data;
      showBadge(kind, t("profile.fileSaved"));
    } else {
      fileErrors.value[kind] = fileError(kind, answer.data);
    }
  } catch {
    fileErrors.value[kind] = t("form.unreachable");
  } finally {
    sending.value = null;
  }
}

// Removes a file of the profile, after a confirmation
async function dropFile(kind: ProfileFileField): Promise<void> {
  if (!window.confirm(t("profile.confirmRemove"))) return;
  fileErrors.value[kind] = undefined;
  sending.value = kind;
  try {
    const answer = await removeFile<Profile>(kind);
    if (answer.status === 200 && answer.data) {
      profile.value = answer.data;
      showBadge(kind, t("profile.fileRemoved"));
    } else {
      fileErrors.value[kind] = fileError(kind, answer.data);
    }
  } catch {
    fileErrors.value[kind] = t("form.unreachable");
  } finally {
    sending.value = null;
  }
}

// Adds a further document of a candidate
async function sendDocument(event: Event): Promise<void> {
  fileErrors.value.document = undefined;
  const file = chosenFile(event, "document");
  if (!file || !candidate.value) return;
  sending.value = "document";
  try {
    const answer = await addDocument(file);
    if (answer.status === 201 && answer.data) {
      candidate.value.documents.push(answer.data);
      showBadge("document", t("profile.fileSaved"));
    } else {
      fileErrors.value.document = fileError("document", answer.data);
    }
  } catch {
    fileErrors.value.document = t("form.unreachable");
  } finally {
    sending.value = null;
  }
}

// Removes a document, after a confirmation
async function dropDocument(id: number): Promise<void> {
  if (!window.confirm(t("profile.confirmRemove")) || !candidate.value) return;
  fileErrors.value.document = undefined;
  sending.value = "document";
  try {
    const answer = await removeDocument(id);
    if (answer.status === 204) {
      candidate.value.documents = candidate.value.documents.filter((d) => d.id !== id);
      showBadge("document", t("profile.fileRemoved"));
    } else {
      fileErrors.value.document = fileError("document", answer.data);
    }
  } catch {
    fileErrors.value.document = t("form.unreachable");
  } finally {
    sending.value = null;
  }
}

// A date of the API, shown in the language of the interface
function formatDate(value: string): string {
  return new Date(value).toLocaleDateString(locale.value);
}

// ── The account: e-mail address ───────────────────────────────────────

// The new address waiting for its link to be opened, if any
const pendingEmail = ref<string | null>(null);
// What the user types, the errors by field, a call in flight, and whether
// the e-mail has just been sent
const newEmail = ref("");
const emailErrors = ref<Record<string, string>>({});
const emailSending = ref(false);
const emailSent = ref(false);

// Keeps, from the addresses of the account, the one not verified yet
function keepPending(addresses: EmailAddressInfo[]): void {
  pendingEmail.value = addresses.find((address) => !address.verified)?.email ?? null;
}

// Reads the addresses once the profile is loaded, to show a pending change
// made earlier. The page works without it.
async function loadEmails(): Promise<void> {
  try {
    const answer = await listEmails();
    if (answer.status === 200 && answer.data) keepPending(answer.data);
  } catch {
    // Nothing to show, then
  }
}

async function submitEmail(): Promise<void> {
  emailErrors.value = {};
  emailSent.value = false;
  emailSending.value = true;
  try {
    const answer = await changeEmail(newEmail.value);
    if (answer.status === 200 && answer.data) {
      keepPending(answer.data);
      emailSent.value = true;
      newEmail.value = "";
    } else if (answer.status === 429) {
      emailErrors.value = { "": t("form.tooMany") };
    } else if (answer.errors) {
      emailErrors.value = errorsByParam(answer.errors);
    } else {
      emailErrors.value = { "": t("form.failed") };
    }
  } catch {
    emailErrors.value = { "": t("form.unreachable") };
  } finally {
    emailSending.value = false;
  }
}

// Drops the pending address: the current one simply stays
async function cancelEmail(): Promise<void> {
  if (!pendingEmail.value) return;
  emailErrors.value = {};
  emailSent.value = false;
  emailSending.value = true;
  try {
    const answer = await cancelEmailChange(pendingEmail.value);
    if (answer.status === 200 && answer.data) {
      keepPending(answer.data);
    } else {
      emailErrors.value = { "": t("form.failed") };
    }
  } catch {
    emailErrors.value = { "": t("form.unreachable") };
  } finally {
    emailSending.value = false;
  }
}

// ── The account: password ─────────────────────────────────────────────

const passwords = reactive({ current: "", next: "", confirm: "" });
const passwordErrors = ref<Record<string, string>>({});
const passwordSending = ref(false);

async function submitPassword(): Promise<void> {
  passwordErrors.value = {};
  // The only check made here: the API receives the new password once
  if (passwords.next !== passwords.confirm) {
    passwordErrors.value = { confirm: t("form.passwordMismatch") };
    return;
  }
  passwordSending.value = true;
  try {
    const answer = await changePassword(passwords.current, passwords.next);
    if (answer.status === 200) {
      Object.assign(passwords, { current: "", next: "", confirm: "" });
      showBadge("password", t("profile.passwordChanged"));
    } else if (answer.status === 429) {
      passwordErrors.value = { "": t("form.tooMany") };
    } else if (answer.errors) {
      // By field: current_password, new_password
      passwordErrors.value = errorsByParam(answer.errors);
    } else {
      passwordErrors.value = { "": t("form.failed") };
    }
  } catch {
    passwordErrors.value = { "": t("form.unreachable") };
  } finally {
    passwordSending.value = false;
  }
}
</script>

<template>
  <h1>{{ t("profile.title") }}</h1>

  <p v-if="loadFailed" class="error">{{ t("profile.loadFailed") }}</p>

  <template v-else-if="profile && session.user">
    <!-- The text fields, saved together -->
    <form novalidate @submit.prevent="save">
      <p v-if="errors['']" class="error">{{ errors[""] }}</p>

      <!-- Identity: the photo of a candidate on the left, the names on the right -->
      <section class="section">
        <h2>{{ t("profile.identity") }}</h2>
        <div class="identity" :class="{ 'with-picture': candidate }">
          <div v-if="candidate" class="portrait">
            <img v-if="candidate.photo" :src="candidate.photo" alt="" class="photo" />
            <span v-else class="photo placeholder" aria-hidden="true">{{ initials }}</span>
            <p class="file-actions">
              <label class="primary">
                {{ candidate.photo ? t("profile.replace") : t("profile.choose") }}
                <input
                  type="file"
                  :accept="ACCEPTED.photo.join(',')"
                  :disabled="sending === 'photo'"
                  hidden
                  @change="sendFile($event, 'photo')"
                />
              </label>
              <button
                v-if="candidate.photo"
                type="button"
                class="secondary"
                :disabled="sending === 'photo'"
                @click="dropFile('photo')"
              >
                {{ t("profile.remove") }}
              </button>
              <span v-if="sending === 'photo'" class="muted">{{ t("profile.sending") }}</span>
              <span v-if="badges.photo" :key="badges.photo.id" class="badge">{{ badges.photo.text }}</span>
            </p>
            <p class="muted rules">{{ t("profile.rules", { types: types("photo"), size: sizeInMb }) }}</p>
            <p v-if="fileErrors.photo" class="error">{{ fileErrors.photo }}</p>
          </div>
          <div class="fields stacked">
            <div v-for="field in IDENTITY_FIELDS" :key="field.key" class="field">
              <label :for="field.key">{{ t(field.label) }}</label>
              <input
                :id="field.key"
                v-model="fields[field.key]"
                type="text"
                :autocomplete="field.autocomplete"
              />
              <p v-if="errors[field.key]" class="error">{{ errors[field.key] }}</p>
            </div>
          </div>
        </div>
      </section>

      <section class="section">
        <h2>{{ t("profile.contact") }}</h2>
        <div class="fields">
          <div
            v-for="field in CONTACT_FIELDS"
            :key="field.key"
            class="field"
            :class="{ wide: field.wide }"
          >
            <label :for="field.key">{{ t(field.label) }}</label>
            <select
              v-if="field.country"
              :id="field.key"
              v-model="fields[field.key]"
              :autocomplete="field.autocomplete"
            >
              <option value="">{{ t("profile.noCountry") }}</option>
              <option v-for="(item, i) in countries" :key="i" :value="item.code">
                {{ item.name }}
              </option>
            </select>
            <input
              v-else
              :id="field.key"
              v-model="fields[field.key]"
              type="text"
              :autocomplete="field.autocomplete"
            />
            <p v-if="errors[field.key]" class="error">{{ errors[field.key] }}</p>
          </div>
        </div>
      </section>

      <!-- Company of an employer: the logo on the left, the fields on the right -->
      <section v-if="employer" class="section">
        <h2>{{ t("profile.company") }}</h2>
        <div class="identity with-picture">
          <div class="portrait">
            <img v-if="employer.logo" :src="employer.logo" alt="" class="logo" />
            <span v-else class="logo placeholder muted">{{ t("profile.noFile") }}</span>
            <p class="file-actions">
              <label class="primary">
                {{ employer.logo ? t("profile.replace") : t("profile.choose") }}
                <input
                  type="file"
                  :accept="ACCEPTED.logo.join(',')"
                  :disabled="sending === 'logo'"
                  hidden
                  @change="sendFile($event, 'logo')"
                />
              </label>
              <button
                v-if="employer.logo"
                type="button"
                class="secondary"
                :disabled="sending === 'logo'"
                @click="dropFile('logo')"
              >
                {{ t("profile.remove") }}
              </button>
              <span v-if="sending === 'logo'" class="muted">{{ t("profile.sending") }}</span>
              <span v-if="badges.logo" :key="badges.logo.id" class="badge">{{ badges.logo.text }}</span>
            </p>
            <p class="muted rules">{{ t("profile.rules", { types: types("logo"), size: sizeInMb }) }}</p>
            <p v-if="fileErrors.logo" class="error">{{ fileErrors.logo }}</p>
          </div>
          <div class="fields">
            <div
              v-for="field in COMPANY_FIELDS"
              :key="field.key"
              class="field"
              :class="{ wide: field.wide }"
            >
              <label :for="field.key">{{ t(field.label) }}</label>
              <select
                v-if="field.country"
                :id="field.key"
                v-model="fields[field.key]"
                :autocomplete="field.autocomplete"
              >
                <option value="">{{ t("profile.noCountry") }}</option>
                <option v-for="(item, i) in countries" :key="i" :value="item.code">
                  {{ item.name }}
                </option>
              </select>
              <input
                v-else
                :id="field.key"
                v-model="fields[field.key]"
                type="text"
                :autocomplete="field.autocomplete"
              />
              <p v-if="errors[field.key]" class="error">{{ errors[field.key] }}</p>
            </div>
          </div>
        </div>
      </section>

      <p class="actions">
        <button type="submit" class="primary" :disabled="saving">
          {{ t("profile.save") }}
        </button>
        <span v-if="badges.form" :key="badges.form.id" class="badge">{{ badges.form.text }}</span>
      </p>
    </form>

    <!-- The documents of a candidate: the CV, and the further documents -->
    <section v-if="candidate" class="section">
      <h2>{{ t("profile.files") }}</h2>
      <div class="columns">
        <div>
          <h3>{{ t("profile.cv") }}</h3>
          <p v-if="candidate.cv">
            <a :href="candidate.cv" target="_blank" rel="noopener">{{ fileName(candidate.cv) }}</a>
          </p>
          <p v-else class="muted">{{ t("profile.noFile") }}</p>
          <p class="file-actions">
            <label class="primary">
              {{ candidate.cv ? t("profile.replace") : t("profile.choose") }}
              <input
                type="file"
                :accept="ACCEPTED.cv.join(',')"
                :disabled="sending === 'cv'"
                hidden
                @change="sendFile($event, 'cv')"
              />
            </label>
            <button
              v-if="candidate.cv"
              type="button"
              class="secondary"
              :disabled="sending === 'cv'"
              @click="dropFile('cv')"
            >
              {{ t("profile.remove") }}
            </button>
            <span v-if="sending === 'cv'" class="muted">{{ t("profile.sending") }}</span>
            <span v-if="badges.cv" :key="badges.cv.id" class="badge">{{ badges.cv.text }}</span>
          </p>
          <p class="muted rules">{{ t("profile.rules", { types: types("cv"), size: sizeInMb }) }}</p>
          <p v-if="fileErrors.cv" class="error">{{ fileErrors.cv }}</p>
        </div>

        <div>
          <h3>{{ t("profile.documents") }}</h3>
          <ul v-if="candidate.documents.length" class="documents">
            <li v-for="document in candidate.documents" :key="document.id">
              <a :href="document.file" target="_blank" rel="noopener">{{ document.name }}</a>
              <span class="muted">{{ t("profile.addedOn", { date: formatDate(document.uploaded_at) }) }}</span>
              <button
                type="button"
                class="as-link"
                :disabled="sending === 'document'"
                @click="dropDocument(document.id)"
              >
                {{ t("profile.remove") }}
              </button>
            </li>
          </ul>
          <p v-else class="muted">{{ t("profile.noFile") }}</p>
          <p class="file-actions">
            <label v-if="candidate.documents.length < MAX_DOCUMENTS" class="primary">
              {{ t("profile.add") }}
              <input
                type="file"
                :accept="ACCEPTED.document.join(',')"
                :disabled="sending === 'document'"
                hidden
                @change="sendDocument"
              />
            </label>
            <span v-else class="muted">{{ t("profile.limit", { max: MAX_DOCUMENTS }) }}</span>
            <span v-if="sending === 'document'" class="muted">{{ t("profile.sending") }}</span>
            <span v-if="badges.document" :key="badges.document.id" class="badge">{{ badges.document.text }}</span>
          </p>
          <p class="muted rules">{{ t("profile.rules", { types: types("document"), size: sizeInMb }) }}</p>
          <p v-if="fileErrors.document" class="error">{{ fileErrors.document }}</p>
        </div>
      </div>
    </section>

    <!-- The account: the address, changed through a confirmation link, and
         the password, changed with the current one -->
    <section class="section">
      <h2>{{ t("profile.account") }}</h2>
      <div class="columns">
        <form novalidate @submit.prevent="submitEmail">
          <h3>{{ t("profile.email") }}</h3>
          <p>{{ t("profile.currentEmail", { email: profile.email }) }}</p>
          <p v-if="emailSent" class="notice">{{ t("profile.emailSent") }}</p>
          <p v-if="pendingEmail" class="pending">
            {{ t("profile.emailPending", { email: pendingEmail }) }}
            <button type="button" class="as-link" :disabled="emailSending" @click="cancelEmail">
              {{ t("profile.cancel") }}
            </button>
          </p>
          <p v-if="emailErrors['']" class="error">{{ emailErrors[""] }}</p>
          <div class="field">
            <label for="new-email">{{ t("profile.newEmail") }}</label>
            <input id="new-email" v-model="newEmail" type="email" autocomplete="email" />
            <p v-if="emailErrors.email" class="error">{{ emailErrors.email }}</p>
          </div>
          <button type="submit" class="primary" :disabled="emailSending">
            {{ t("profile.changeEmail") }}
          </button>
        </form>

        <form novalidate @submit.prevent="submitPassword">
          <h3>{{ t("profile.password") }}</h3>
          <p v-if="passwordErrors['']" class="error">{{ passwordErrors[""] }}</p>
          <div class="field">
            <label for="current-password">{{ t("profile.currentPassword") }}</label>
            <input
              id="current-password"
              v-model="passwords.current"
              type="password"
              autocomplete="current-password"
            />
            <p v-if="passwordErrors.current_password" class="error">
              {{ passwordErrors.current_password }}
            </p>
          </div>
          <div class="field">
            <label for="new-password">{{ t("profile.newPassword") }}</label>
            <input
              id="new-password"
              v-model="passwords.next"
              type="password"
              autocomplete="new-password"
            />
            <p v-if="passwordErrors.new_password" class="error">
              {{ passwordErrors.new_password }}
            </p>
          </div>
          <div class="field">
            <label for="new-password-confirm">{{ t("profile.newPasswordConfirm") }}</label>
            <input
              id="new-password-confirm"
              v-model="passwords.confirm"
              type="password"
              autocomplete="new-password"
            />
            <p v-if="passwordErrors.confirm" class="error">{{ passwordErrors.confirm }}</p>
          </div>
          <p class="actions">
            <button type="submit" class="primary" :disabled="passwordSending">
              {{ t("profile.changePassword") }}
            </button>
            <span v-if="badges.password" :key="badges.password.id" class="badge">
              {{ badges.password.text }}
            </span>
          </p>
        </form>
      </div>
    </section>
  </template>
</template>

<style scoped>
/* A section of the page, separated from the previous one by a rule */
.section {
  padding: 12px 0 8px;
  border-top: 1px solid var(--mt-border);
}

h2 {
  margin: 8px 0 12px;
  font-size: 1.15rem;
}

h3 {
  margin: 8px 0 8px;
  font-size: 1rem;
}

.muted {
  color: var(--mt-muted);
}

/* The fields of a section on two columns; a wide field takes the row */
.fields {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0 24px;
}

.fields .wide {
  grid-column: 1 / -1;
}

/* The names, one under the other, beside the picture */
.fields.stacked {
  grid-template-columns: minmax(0, 1fr);
  max-width: 520px;
}

.fields .field input,
.fields .field select {
  max-width: none;
}

/* The fields of a section, with a picture on their left when there is
   one (the photo of a candidate, the logo of a company) */
.identity {
  display: grid;
  grid-template-columns: minmax(0, 1fr);
  gap: 8px 32px;
  align-items: start;
}

.identity.with-picture {
  grid-template-columns: 240px minmax(0, 1fr);
}

/* Two blocks side by side, each with its own title */
.columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 48px;
  align-items: start;
}

/* The photo of a candidate: a round; without one, the initials */
.photo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  border: 1px solid var(--mt-border);
  border-radius: 50%;
  object-fit: cover;
}

/* The logo of an employer: a square, the picture kept whole inside */
.logo {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 140px;
  height: 140px;
  padding: 8px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  object-fit: contain;
  font-size: 0.85rem;
  text-align: center;
}

.placeholder {
  background: var(--mt-surface);
  color: var(--mt-muted);
  font-size: 2rem;
  font-weight: 600;
}

/* A button and its confirmation, side by side */
.actions {
  display: flex;
  align-items: center;
  gap: 12px;
  margin: 16px 0;
}

/* A confirmation: a check mark and a few words in a green pill, shown at
   once, kept, then faded away over its last second. The animation runs
   once; the element is removed from the page when it ends. */
.badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 2px 10px;
  border-radius: 999px;
  background: var(--mt-success-surface);
  color: var(--mt-success);
  font-size: 0.9rem;
  animation: badge 3s ease forwards;
}

.badge::before {
  content: "✓";
  font-weight: 600;
}

@keyframes badge {
  0% {
    opacity: 0;
    transform: translateY(4px);
  }
  10% {
    opacity: 1;
    transform: none;
  }
  70% {
    opacity: 1;
  }
  100% {
    opacity: 0;
  }
}

/* The buttons of a file, side by side; a label styled as the main button
   opens the file dialog of its hidden input */
.file-actions {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 12px;
  margin: 12px 0 0;
}

.file-actions label.primary {
  display: inline-block;
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

.secondary:disabled {
  opacity: 0.6;
  cursor: default;
}

.rules {
  margin: 4px 0 0;
  font-size: 0.9rem;
}

/* One document per line: its name, its date, the way to remove it */
.documents {
  margin: 0;
  padding: 0;
  list-style: none;
}

.documents li {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  gap: 12px;
  padding: 6px 0;
}

/* The address waiting for its link, with the way to give it up */
.pending {
  color: var(--mt-muted);
}

.pending .as-link {
  margin-left: 8px;
}

/* Narrow window: one column everywhere */
@media (max-width: 720px) {
  .fields,
  .identity.with-picture,
  .columns {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
