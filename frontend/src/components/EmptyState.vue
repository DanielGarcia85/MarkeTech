<!--
  frontend/src/components/EmptyState.vue

  Empty state — what a list shows when it has nothing to show
  ───────────────────────────────────────────────────────────────────────────
  Used by the lists of the site (the offers, the favorites, the
  applications of a candidate, the offers and the applications of an
  employer) instead of a bare sentence: a drawing (Icon) in a disc of the
  light blue, the sentence of the page under it and, when the page gives
  one in the slot, a link to the place where the list gets filled.
-->

<script setup lang="ts">
import Icon, { type IconName } from "./Icon.vue";

defineProps<{
  icon: IconName;
  text: string;
}>();
</script>

<template>
  <div class="empty">
    <span class="disc">
      <Icon :name="icon" :size="30" />
    </span>
    <p class="text">{{ text }}</p>
    <p v-if="$slots.default" class="action"><slot /></p>
  </div>
</template>

<style scoped>
/* Centred, with air around, in a dashed frame of the light blue */
.empty {
  margin: 16px 0;
  padding: 36px 16px;
  border: 1px dashed var(--mt-blue-border);
  border-radius: 12px;
  text-align: center;
}

.disc {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  background: var(--mt-blue-surface);
  color: var(--mt-blue);
}

.text {
  max-width: 480px;
  margin: 14px auto 0;
  color: var(--mt-muted);
}

.action {
  margin: 12px 0 0;
}
</style>
