<!--
  frontend/src/components/FavoriteButton.vue

  Favorite button — the heart that puts an offer aside
  ───────────────────────────────────────────────────────────────────────────
  Used on the cards of the offers and on the page of an offer. For a
  candidate, a button whose heart is filled when the offer is among their
  favorites and empty otherwise; a click calls the API and tells the parent
  the new state, which keeps the offer up to date. For a visitor, a link to
  the login page that comes back here afterwards. For an employer, nothing.
  The heart is drawn in SVG, the colour of the errors when filled.
-->

<script setup lang="ts">
import { computed, ref } from "vue";
import { useI18n } from "vue-i18n";
import { useRoute } from "vue-router";

import { addFavorite, removeFavorite } from "../api/favorites";
import type { Offer } from "../api/offers";
import { useSession } from "../session";

const props = defineProps<{ offer: Offer }>();

// The new state of the offer, once the API agreed
const emit = defineEmits<{ change: [favorite: boolean] }>();

const { t } = useI18n();
const route = useRoute();
const session = useSession();

const role = computed(() => session.user?.role ?? null);
// A call in flight: the button is disabled meanwhile
const busy = ref(false);

const label = computed(() =>
  props.offer.favorite ? t("favorites.remove") : t("favorites.add"),
);

async function toggle(): Promise<void> {
  busy.value = true;
  try {
    const wanted = !props.offer.favorite;
    const answer = wanted ? await addFavorite(props.offer.id) : await removeFavorite(props.offer.id);
    // 201 added, 204 removed; a 400 "already" or a 404 "not any more" means
    // the state was stale: the wanted state holds either way
    if ([201, 204, 400, 404].includes(answer.status)) emit("change", wanted);
  } catch {
    // The server could not be reached: the heart stays as it was
  } finally {
    busy.value = false;
  }
}
</script>

<template>
  <button
    v-if="role === 'candidate'"
    type="button"
    class="heart"
    :class="{ on: offer.favorite }"
    :aria-pressed="offer.favorite"
    :aria-label="label"
    :title="label"
    :disabled="busy"
    @click="toggle"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 21s-7.5-4.7-9.5-9.2C1.1 8.6 3 5 6.6 5c2 0 3.4 1.1 4.2 2.4h2.4C14 6.1 15.4 5 17.4 5 21 5 22.9 8.6 21.5 11.8 19.5 16.3 12 21 12 21z"
      />
    </svg>
  </button>
  <RouterLink
    v-else-if="role === null"
    :to="{ name: 'login', query: { next: route.fullPath } }"
    class="heart"
    :aria-label="t('favorites.loginToSave')"
    :title="t('favorites.loginToSave')"
  >
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path
        d="M12 21s-7.5-4.7-9.5-9.2C1.1 8.6 3 5 6.6 5c2 0 3.4 1.1 4.2 2.4h2.4C14 6.1 15.4 5 17.4 5 21 5 22.9 8.6 21.5 11.8 19.5 16.3 12 21 12 21z"
      />
    </svg>
  </RouterLink>
</template>

<style scoped>
/* A round button holding the heart; the outline in the muted colour,
   filled in the colour of the errors (a red) when the offer is put aside */
.heart {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  padding: 0;
  border: 1px solid var(--mt-border);
  border-radius: 50%;
  background: var(--mt-background);
  color: var(--mt-muted);
  cursor: pointer;
}

.heart:hover {
  color: var(--mt-error);
}

.heart:disabled {
  opacity: 0.6;
  cursor: default;
}

.heart svg {
  width: 20px;
  height: 20px;
  fill: none;
  stroke: currentColor;
  stroke-width: 2;
  stroke-linejoin: round;
}

.heart.on {
  border-color: var(--mt-error);
  color: var(--mt-error);
}

.heart.on svg {
  fill: currentColor;
}
</style>
