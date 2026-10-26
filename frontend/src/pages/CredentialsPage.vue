<!--
  frontend/src/pages/CredentialsPage.vue

  Credentials page — the e-mail address and the password of the account
  ───────────────────────────────────────────────────────────────────────────
  Displayed for "/account/credentials", for a logged-in user only: the
  router sends a visitor to the login page. What the user logs in with,
  kept apart from the profile (names, contact details, files): a new
  e-mail address, confirmed by a link sent to it, the current one staying
  in force until then and the pending one shown with the way to give it
  up; and a new password, given with the current one. Two forms side by
  side on a wide window, one under the other on a narrow one. The
  password changed shows a short confirmation next to its button. On a
  demo account, both forms are shown disabled (the server refuses the
  changes anyway: demo/middleware.py). Under them, for a candidate or an
  employer, the notifications: one box, ticked by default, that turns the
  notification e-mails on or off, saved at once with a short confirmation
  (the profile API; decisions of 26.10.2026), one generic sentence as its
  label, the details being on the privacy page. A demo account receives no
  e-mail: the box is shown unticked and disabled, with a line that says so.
-->

<script setup lang="ts">
import { computed, reactive, ref } from "vue";
import { useI18n } from "vue-i18n";

import {
  cancelEmailChange,
  changeEmail,
  changePassword,
  listEmails,
  type EmailAddressInfo,
} from "../api/account";
import { errorsByParam } from "../api/http";
import { getProfile, updateProfile } from "../api/profile";
import { useSession } from "../session";

const { t } = useI18n();
const session = useSession();

// A demo account keeps its address and its password
const locked = computed(() => session.user?.is_demo === true);

// ── The e-mail address ────────────────────────────────────────────────

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

// Reads the addresses when the page opens, to show a pending change made
// earlier. The page works without it.
async function loadEmails(): Promise<void> {
  try {
    const answer = await listEmails();
    if (answer.status === 200 && answer.data) keepPending(answer.data);
  } catch {
    // Nothing to show, then
  }
}

// Runs once, when the page opens: the router has already made sure that
// someone is logged in
loadEmails();

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

// ── The password ──────────────────────────────────────────────────────

const passwords = reactive({ current: "", next: "", confirm: "" });
const passwordErrors = ref<Record<string, string>>({});
const passwordSending = ref(false);

// The confirmation shown next to the button once the password is changed:
// its text, and a number that changes at every showing, so that the
// animation starts again when it is changed twice in a row
const badge = ref<{ text: string; id: number } | null>(null);
const BADGE_DURATION = 3000;
let badgeId = 0;
let badgeTimer = 0;

function showBadge(text: string): void {
  badge.value = { text, id: ++badgeId };
  // A confirmation replaces the previous one, and leaves after its time
  window.clearTimeout(badgeTimer);
  badgeTimer = window.setTimeout(() => {
    badge.value = null;
  }, BADGE_DURATION);
}

// ── The notifications ─────────────────────────────────────────────────

// Whether the account receives them; null until read, or for a user
// without a role (an administrator has no profile)
const notify = ref<boolean | null>(null);
const notifySaving = ref(false);
const notifyError = ref("");
const notifyBadge = ref<{ text: string; id: number } | null>(null);
let notifyTimer = 0;

async function loadNotify(): Promise<void> {
  if (!session.user?.role) return;
  try {
    notify.value = (await getProfile()).notify_by_email;
  } catch {
    // The section stays hidden
  }
}

loadNotify();

// Saved as soon as the box changes; put back if the server refuses
async function saveNotify(event: Event): Promise<void> {
  const wanted = (event.target as HTMLInputElement).checked;
  notifyError.value = "";
  notifySaving.value = true;
  try {
    const answer = await updateProfile({ notify_by_email: wanted });
    if (answer.status === 200) {
      notify.value = wanted;
      notifyBadge.value = { text: t("credentials.notifySaved"), id: ++badgeId };
      window.clearTimeout(notifyTimer);
      notifyTimer = window.setTimeout(() => (notifyBadge.value = null), BADGE_DURATION);
    } else {
      notifyError.value = t("form.failed");
    }
  } catch {
    notifyError.value = t("form.unreachable");
  } finally {
    notifySaving.value = false;
    // The box shows what the server holds
    (event.target as HTMLInputElement).checked = notify.value ?? wanted;
  }
}

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
      showBadge(t("credentials.passwordChanged"));
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
  <h1>{{ t("credentials.title") }}</h1>

  <p v-if="locked" class="notice">{{ t("demo.locked") }}</p>

  <div v-if="session.user" class="columns">
    <!-- The address, changed through a confirmation link -->
    <form novalidate class="section" @submit.prevent="submitEmail">
      <fieldset :disabled="locked">
      <h2>{{ t("credentials.email") }}</h2>
      <p>{{ t("credentials.currentEmail", { email: session.user.email }) }}</p>
      <p v-if="emailSent" class="notice">{{ t("credentials.emailSent") }}</p>
      <p v-if="pendingEmail" class="pending">
        {{ t("credentials.emailPending", { email: pendingEmail }) }}
        <button type="button" class="as-link" :disabled="emailSending" @click="cancelEmail">
          {{ t("credentials.cancel") }}
        </button>
      </p>
      <p v-if="emailErrors['']" class="error">{{ emailErrors[""] }}</p>
      <div class="field">
        <label for="new-email">{{ t("credentials.newEmail") }}</label>
        <input id="new-email" v-model="newEmail" type="email" autocomplete="email" />
        <p v-if="emailErrors.email" class="error">{{ emailErrors.email }}</p>
      </div>
      <button type="submit" class="primary" :disabled="emailSending">
        {{ t("credentials.changeEmail") }}
      </button>
      </fieldset>
    </form>

    <!-- The password, changed with the current one -->
    <form novalidate class="section" @submit.prevent="submitPassword">
      <fieldset :disabled="locked">
      <h2>{{ t("credentials.password") }}</h2>
      <p v-if="passwordErrors['']" class="error">{{ passwordErrors[""] }}</p>
      <div class="field">
        <label for="current-password">{{ t("credentials.currentPassword") }}</label>
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
        <label for="new-password">{{ t("credentials.newPassword") }}</label>
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
        <label for="new-password-confirm">{{ t("credentials.newPasswordConfirm") }}</label>
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
          {{ t("credentials.changePassword") }}
        </button>
        <span v-if="badge" :key="badge.id" class="badge">{{ badge.text }}</span>
      </p>
      </fieldset>
    </form>
  </div>

  <!-- The notification e-mails, for a candidate or an employer -->
  <section v-if="notify !== null" class="section notifications">
    <h2>{{ t("credentials.notifications") }}</h2>
    <p class="actions">
      <label class="check">
        <input
          type="checkbox"
          :checked="notify && !locked"
          :disabled="locked || notifySaving"
          @change="saveNotify"
        />
        {{ t("credentials.notify") }}
      </label>
      <span v-if="notifyBadge" :key="notifyBadge.id" class="badge">{{ notifyBadge.text }}</span>
    </p>
    <p v-if="locked" class="hint">{{ t("credentials.notifyDemo") }}</p>
    <p v-if="notifyError" class="error">{{ notifyError }}</p>
  </section>
</template>

<style scoped>
/* The two forms side by side, each with its own title */
.columns {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px 48px;
  align-items: start;
}

/* A form of the page, under a rule, as the sections of the profile */
.section {
  padding: 12px 0 8px;
  border-top: 1px solid var(--mt-border);
}

/* The title of a form: the only text in the brand colour, so that the
   eye finds the two parts first */
h2 {
  margin: 10px 0 16px;
  color: var(--mt-blue);
  font-size: 1.35rem;
}

/* The frame that disables a whole form at once, without a look of its own */
fieldset {
  margin: 0;
  padding: 0;
  border: none;
}

/* Disabled (a demo account): the fields greyed like the buttons */
fieldset:disabled input {
  background: var(--mt-surface);
  cursor: not-allowed;
}

/* The address waiting for its link, with the way to give it up */
.pending {
  color: var(--mt-muted);
}

.pending .as-link {
  margin-left: 8px;
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

/* The notifications, under the two forms, across the page */
.notifications {
  margin-top: 16px;
}

.hint {
  margin: 0 0 8px;
  color: var(--mt-muted);
}

/* The box and its words on one line */
.check {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.check input {
  width: 18px;
  height: 18px;
  margin: 0;
}

/* Narrow window: one form under the other */
@media (max-width: 720px) {
  .columns {
    grid-template-columns: minmax(0, 1fr);
  }
}
</style>
