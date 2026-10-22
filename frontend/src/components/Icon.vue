<!--
  frontend/src/components/Icon.vue

  Icon — one of the small drawings of the site, by its name
  ───────────────────────────────────────────────────────────────────────────
  Used by the side bar before each link, and by the empty states of the
  lists. Line drawings on a 24 × 24 grid, drawn in the colour of the text
  around them (currentColor), so that they follow the link they sit in.
  Decorative: hidden from screen readers, the text next to them says it
  all. The names are typed: a misspelled one is a type error.
-->

<script lang="ts">
export type IconName =
  | "briefcase"
  | "clipboard"
  | "inbox"
  | "send"
  | "heart"
  | "user"
  | "key"
  | "search"
  | "chat"
  | "archive"
  | "calendar";
</script>

<script setup lang="ts">
withDefaults(
  defineProps<{
    name: IconName;
    // The side of the drawing, in pixels
    size?: number;
  }>(),
  { size: 18 },
);
</script>

<template>
  <svg
    :width="size"
    :height="size"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    stroke-width="1.8"
    stroke-linecap="round"
    stroke-linejoin="round"
    aria-hidden="true"
    class="icon"
  >
    <!-- A case with a handle: the offers -->
    <g v-if="name === 'briefcase'">
      <rect x="3" y="7" width="18" height="13" rx="2" />
      <path d="M8 7V5a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
      <path d="M3 12h18" />
    </g>
    <!-- A board with lines: the offers of an employer -->
    <g v-else-if="name === 'clipboard'">
      <rect x="5" y="4" width="14" height="17" rx="2" />
      <path d="M9 4V3h6v1" />
      <path d="M9 10h6M9 14h6" />
    </g>
    <!-- A tray: the applications received -->
    <g v-else-if="name === 'inbox'">
      <path d="M5.5 5h13L21 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-6z" />
      <path d="M3 13h5l2 3h4l2-3h5" />
    </g>
    <!-- A paper plane: the applications sent -->
    <g v-else-if="name === 'send'">
      <path d="M21 3L10 14" />
      <path d="M21 3l-7 18-4-7-7-4z" />
    </g>
    <!-- A heart: the favorites -->
    <path v-else-if="name === 'heart'" d="M12 20s-7-4.5-7-10a4 4 0 0 1 7-2.5A4 4 0 0 1 19 10c0 5.5-7 10-7 10z" />
    <!-- A head and shoulders: the profile -->
    <g v-else-if="name === 'user'">
      <circle cx="12" cy="8" r="4" />
      <path d="M4 20a8 8 0 0 1 16 0" />
    </g>
    <!-- A key: the credentials -->
    <g v-else-if="name === 'key'">
      <circle cx="8" cy="15" r="4" />
      <path d="M10.8 12.2L20 3" />
      <path d="M17 6l2.5 2.5M14 9l2.5 2.5" />
    </g>
    <!-- A speech bubble: the open conversations -->
    <path v-else-if="name === 'chat'" d="M4 5h16v11H9l-5 4z" />
    <!-- A box with its lid: the closed conversations -->
    <g v-else-if="name === 'archive'">
      <rect x="3" y="4" width="18" height="4" rx="1" />
      <path d="M5 8v11h14V8" />
      <path d="M10 12h4" />
    </g>
    <!-- A leaf of a calendar: the appointments -->
    <g v-else-if="name === 'calendar'">
      <rect x="3" y="5" width="18" height="16" rx="2" />
      <path d="M3 10h18M8 3v4M16 3v4" />
    </g>
    <!-- A magnifying glass: a search without result -->
    <g v-else-if="name === 'search'">
      <circle cx="11" cy="11" r="6" />
      <path d="M20 20l-4.5-4.5" />
    </g>
  </svg>
</template>

<style scoped>
/* Sits on the line of the text, never shrinks beside it */
.icon {
  flex: none;
  vertical-align: -3px;
}
</style>
