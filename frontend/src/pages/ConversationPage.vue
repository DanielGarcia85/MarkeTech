<!--
  frontend/src/pages/ConversationPage.vue

  Conversation page — the messages of one application, read and written
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/messages/<application id>", to its two
  participants only (anyone else gets "not found" from the API). At the top,
  the way back to the open or closed conversations, the other participant
  with their mark, the offer and the state of the application. Then the
  messages, oldest first, as bubbles: one's own on the right in the light
  blue, the other's on the left. At the bottom, the text area and the Send
  button while the application is in progress; once decided, a line says
  the conversation is closed, and the messages stay readable. Reading the
  page marks the other's messages read (the API does it), after which the
  counts of the side bar are read again (notifications.ts). Read again every ten seconds
  (phase 2: no WebSocket yet).
-->

<script setup lang="ts">
import { computed, nextTick, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { firstErrors } from "../api/http";
import { getThread, writeMessage, type Thread } from "../api/messaging";
import { useApplicationText } from "../applications";
import CompanyMark from "../components/CompanyMark.vue";
import { refreshNotifications } from "../notifications";
import { useSession } from "../session";

const { t, locale } = useI18n();
const route = useRoute();
const session = useSession();
const text = useApplicationText();

const thread = ref<Thread | null>(null);
const notFound = ref(false);

// What the user types, a message in flight, the reason of a refusal
const body = ref("");
const sending = ref(false);
const error = ref("");

// The list of the messages, scrolled to its end when one arrives
const list = ref<HTMLElement | null>(null);

const applicationId = computed(() => Number(route.params.id));
const isCandidate = computed(() => session.user?.role === "candidate");

// The way back: to the list the conversation belongs to
const back = computed(() => (thread.value?.open === false ? "closedConversations" : "conversations"));

async function load(): Promise<void> {
  const count = thread.value?.messages.length ?? 0;
  try {
    thread.value = await getThread(applicationId.value);
  } catch {
    // 404: not a conversation of the user, or no such application
    notFound.value = true;
    return;
  }
  // The other's messages are read now: the side bar counts again
  refreshNotifications();
  if (thread.value.messages.length !== count) scrollDown();
}

async function scrollDown(): Promise<void> {
  await nextTick();
  if (list.value) list.value.scrollTop = list.value.scrollHeight;
}

async function send(): Promise<void> {
  if (!body.value.trim() || !thread.value) return;
  error.value = "";
  sending.value = true;
  try {
    const answer = await writeMessage(thread.value.application, body.value);
    if (answer.status === 201 && answer.data) {
      thread.value.messages.push(answer.data);
      body.value = "";
      scrollDown();
    } else {
      const errors = firstErrors(answer.data as Record<string, string[]> | null);
      error.value = errors.body ?? errors[""] ?? t("form.failed");
      // Closed meanwhile (decided by the employer): read the new state
      load();
    }
  } catch {
    error.value = t("form.unreachable");
  } finally {
    sending.value = false;
  }
}

// Ctrl+Enter (or Cmd+Enter) sends, Enter alone goes to the next line
function keydown(event: KeyboardEvent): void {
  if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) send();
}

// "21 Oct, 14:05", in the language displayed
function when(iso: string): string {
  return new Intl.DateTimeFormat(locale.value, {
    day: "numeric",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(iso));
}

// Another conversation opened from this one: start again
watch(applicationId, () => {
  thread.value = null;
  notFound.value = false;
  load();
});

let timer = 0;
onMounted(() => {
  load();
  timer = window.setInterval(load, 10_000);
});
onUnmounted(() => window.clearInterval(timer));
</script>

<template>
  <p class="back">
    <RouterLink :to="{ name: back }">
      ← {{ back === "conversations" ? t("messaging.openTitle") : t("messaging.closedTitle") }}
    </RouterLink>
  </p>

  <p v-if="notFound" class="notice">{{ t("messaging.notFound") }}</p>

  <template v-else-if="thread">
    <header class="head">
      <CompanyMark :name="thread.other" :logo="isCandidate ? thread.offer.company.logo : null" :size="56" />
      <div class="who">
        <h1>{{ thread.other }}</h1>
        <p>
          <RouterLink :to="{ name: 'offer', params: { id: thread.offer.id } }">{{ thread.offer.title }}</RouterLink>
          <span v-if="!isCandidate" class="muted"> · {{ thread.offer.company.name }}</span>
          <span class="pill" :class="thread.status">{{ text.status(thread.status) }}</span>
        </p>
      </div>
    </header>

    <div ref="list" class="messages">
      <p v-if="thread.messages.length === 0" class="empty">
        {{ thread.open ? t("messaging.emptyOpen") : t("messaging.emptyClosed") }}
      </p>
      <div v-for="message in thread.messages" :key="message.id" class="message" :class="{ mine: message.mine }">
        <p class="bubble">{{ message.body }}</p>
        <p class="meta">
          {{ when(message.sent_at) }}
          <template v-if="message.mine && message.read_at"> · {{ t("messaging.read") }}</template>
        </p>
      </div>
    </div>

    <form v-if="thread.open" class="composer" novalidate @submit.prevent="send">
      <label for="message" class="hidden">{{ t("messaging.placeholder") }}</label>
      <textarea
        id="message"
        v-model="body"
        rows="3"
        maxlength="2000"
        :placeholder="t('messaging.placeholder')"
        @keydown="keydown"
      ></textarea>
      <p class="actions">
        <span class="muted hint">{{ t("messaging.hint") }}</span>
        <button type="submit" class="primary" :disabled="sending || !body.trim()">{{ t("messaging.send") }}</button>
      </p>
      <p v-if="error" class="error">{{ error }}</p>
    </form>
    <p v-else class="closed">{{ t("messaging.closed." + thread.status) }}</p>
  </template>
</template>

<style scoped>
.back {
  margin: 0 0 12px;
}

.back a {
  text-decoration: none;
}

.back a:hover {
  text-decoration: underline;
}

/* The other participant, the offer, the state */
.head {
  display: flex;
  align-items: center;
  gap: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--mt-border);
}

.who h1 {
  margin: 0;
  font-size: 1.5rem;
}

.who p {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 4px 10px;
  margin: 2px 0 0;
}

.muted {
  color: var(--mt-muted);
}

/* The messages, in a column that scrolls on its own once long */
.messages {
  display: flex;
  flex-direction: column;
  gap: 12px;
  max-height: 60vh;
  overflow-y: auto;
  padding: 20px 4px;
}

.empty {
  margin: 24px 0;
  color: var(--mt-muted);
  text-align: center;
}

/* A message: the other's on the left, one's own on the right */
.message {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 75%;
}

.message.mine {
  align-self: flex-end;
  align-items: flex-end;
}

/* The text as typed, its line breaks kept */
.bubble {
  margin: 0;
  padding: 10px 14px;
  border: 1px solid var(--mt-border);
  border-radius: 14px 14px 14px 4px;
  background: var(--mt-background);
  white-space: pre-wrap;
  overflow-wrap: anywhere;
}

.mine .bubble {
  border-color: var(--mt-blue-border);
  border-radius: 14px 14px 4px 14px;
  background: var(--mt-blue-surface);
}

.meta {
  margin: 4px 6px 0;
  color: var(--mt-muted);
  font-size: 0.8rem;
}

/* The text area and the button, under a rule */
.composer {
  padding-top: 16px;
  border-top: 1px solid var(--mt-border);
}

.composer textarea {
  display: block;
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--mt-border);
  border-radius: 8px;
  color: var(--mt-text);
  font: inherit;
  resize: vertical;
}

.actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 16px;
  margin: 10px 0 0;
}

.hint {
  font-size: 0.85rem;
}

/* Read only: the closing line in a box of the light blue */
.closed {
  margin: 0;
  padding: 12px 16px;
  border: 1px solid var(--mt-blue-border);
  border-radius: 8px;
  background: var(--mt-blue-surface);
  text-align: center;
}

/* For the screen readers only: the text area has a label */
.hidden {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip-path: inset(50%);
}

/* The state of the application, as on the other pages */
.pill {
  display: inline-block;
  padding: 1px 10px;
  border: 1px solid var(--mt-border);
  border-radius: 999px;
  background: var(--mt-surface);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

.pill.in_progress {
  border-color: var(--mt-blue);
  color: var(--mt-blue);
}

.pill.accepted {
  border-color: var(--mt-success-surface);
  background: var(--mt-success-surface);
  color: var(--mt-success);
}

.pill.rejected {
  border-color: var(--mt-error);
  color: var(--mt-error);
}

/* Narrow window: the bubbles may take more of the width */
@media (max-width: 600px) {
  .message {
    max-width: 90%;
  }

  .hint {
    display: none;
  }
}
</style>
