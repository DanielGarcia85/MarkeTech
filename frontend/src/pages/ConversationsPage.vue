<!--
  frontend/src/pages/ConversationsPage.vue

  Conversations page — the open or the closed conversations of the user
  ───────────────────────────────────────────────────────────────────────────
  Displayed by the router for "/messages" (the open ones: their applications
  are in progress) and "/messages/closed" (the closed ones: decided, read
  only), to a logged-in user of either role. One line per conversation, the
  most recent activity first: the other participant (the company for a
  candidate, the candidate for an employer) with their mark, the offer, the
  last message, its date and the unread count; the whole line leads to the
  conversation. Read again every minute with the counts of the side bar.
-->

<script setup lang="ts">
import { computed, onMounted, onUnmounted, ref, watch } from "vue";
import { useI18n } from "vue-i18n";

import { listConversations, type Conversation } from "../api/messaging";
import CompanyMark from "../components/CompanyMark.vue";
import EmptyState from "../components/EmptyState.vue";
import { useSession } from "../session";

const props = defineProps<{ closed: boolean }>();

const { t, locale } = useI18n();
const session = useSession();

const conversations = ref<Conversation[] | null>(null);
const loadFailed = ref(false);

// The logo of the company is shown to the candidate; an employer sees the
// initial of the candidate on a colour
const isCandidate = computed(() => session.user?.role === "candidate");

async function load(): Promise<void> {
  loadFailed.value = false;
  try {
    conversations.value = await listConversations(props.closed ? "closed" : "open");
  } catch {
    loadFailed.value = true;
  }
}

// "14:05" today, "20 oct." before, in the language displayed
function when(iso: string): string {
  const date = new Date(iso);
  const today = new Date().toDateString() === date.toDateString();
  const format: Intl.DateTimeFormatOptions = today
    ? { hour: "2-digit", minute: "2-digit" }
    : { day: "numeric", month: "short" };
  return new Intl.DateTimeFormat(locale.value, format).format(date);
}

// From one list to the other: the same page, another kind
watch(() => props.closed, load);

// Read again every minute, like the counts of the side bar
let timer = 0;
onMounted(() => {
  load();
  timer = window.setInterval(load, 60_000);
});
onUnmounted(() => window.clearInterval(timer));
</script>

<template>
  <h1>{{ closed ? t("messaging.closedTitle") : t("messaging.openTitle") }}</h1>

  <p v-if="loadFailed" class="error">{{ t("messaging.loadFailed") }}</p>

  <template v-else-if="conversations">
    <EmptyState
      v-if="conversations.length === 0"
      :icon="closed ? 'archive' : 'chat'"
      :text="closed ? t('messaging.noneClosed') : t('messaging.noneOpen')"
    />
    <ul v-else class="list">
      <li v-for="conversation in conversations" :key="conversation.application">
        <RouterLink
          :to="{ name: 'conversation', params: { id: conversation.application } }"
          class="row"
          :class="{ unread: conversation.unread }"
        >
          <CompanyMark
            :name="conversation.other"
            :logo="isCandidate ? conversation.offer.company.logo : null"
            :size="48"
          />
          <span class="text">
            <span class="top">
              <strong class="other">{{ conversation.other }}</strong>
              <span class="date">{{ when(conversation.last.sent_at) }}</span>
            </span>
            <span class="offer">{{ conversation.offer.title }}</span>
            <span class="last">
              <template v-if="conversation.last.mine">{{ t("messaging.you") }}&nbsp;</template>{{ conversation.last.body }}
            </span>
          </span>
          <span v-if="conversation.unread" class="badge">{{ conversation.unread }}</span>
        </RouterLink>
      </li>
    </ul>
  </template>
</template>

<style scoped>
.list {
  margin: 16px 0 0;
  padding: 0;
  list-style: none;
}

/* One conversation, in a box like the cards, the whole box a link */
.row {
  display: flex;
  align-items: center;
  gap: 16px;
  margin-bottom: 10px;
  padding: 14px 18px;
  border: 1px solid var(--mt-border);
  border-radius: 12px;
  background: var(--mt-background);
  color: var(--mt-text);
  text-decoration: none;
  transition:
    box-shadow 0.15s ease,
    border-color 0.15s ease;
}

.row:hover {
  border-color: var(--mt-blue-border);
  box-shadow: 0 6px 18px rgba(31, 80, 106, 0.1);
}

/* Unread: a band of the accent on the left, the last message in the text
   colour */
.row.unread {
  border-left: 4px solid var(--mt-accent);
}

.text {
  display: flex;
  flex: 1;
  flex-direction: column;
  min-width: 0;
}

.top {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.other {
  font-size: 1.05rem;
}

.date {
  flex: none;
  color: var(--mt-muted);
  font-size: 0.85rem;
}

.offer {
  color: var(--mt-blue);
  font-size: 0.9rem;
}

/* The last message on one line, cut with an ellipsis */
.last {
  overflow: hidden;
  color: var(--mt-muted);
  text-overflow: ellipsis;
  white-space: nowrap;
}

.row.unread .last {
  color: var(--mt-text);
  font-weight: 500;
}

/* The unread count, in the accent colour */
.badge {
  display: inline-flex;
  flex: none;
  align-items: center;
  justify-content: center;
  min-width: 24px;
  height: 24px;
  padding: 0 7px;
  border-radius: 999px;
  background: var(--mt-accent);
  color: #ffffff;
  font-size: 0.8rem;
  font-weight: 600;
}
</style>
