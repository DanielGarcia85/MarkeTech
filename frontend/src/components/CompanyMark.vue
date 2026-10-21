<!--
  frontend/src/components/CompanyMark.vue

  Company mark — the logo of a company, or its initial on a colour
  ───────────────────────────────────────────────────────────────────────────
  Used by the offer cards and by the page of an offer. The logo in a
  square, kept whole with some air around it; without a logo, the first
  letter of the name on a background chosen from the name, so that the
  same company always gets the same colour and a list of offers is not a
  column of grey squares. The side of the square is given by the parent.
-->

<script setup lang="ts">
import { computed } from "vue";

const props = defineProps<{
  name: string;
  logo: string | null;
  // The side of the square, in pixels
  size: number;
}>();

// Six pairs of a light background and a dark text, readable together
const COLOURS = [
  { background: "#dbeafe", color: "#1e3a8a" }, // blue
  { background: "#dcfce7", color: "#166534" }, // green
  { background: "#fdf1dd", color: "#8f4f0b" }, // amber
  { background: "#fce7f3", color: "#9d174d" }, // pink
  { background: "#ede9fe", color: "#5b21b6" }, // violet
  { background: "#ccfbf1", color: "#115e59" }, // teal
];

const initial = computed(() => props.name.trim().charAt(0).toUpperCase() || "?");

// The colour of a name: the codes of its characters added up, the sum
// taken modulo the number of colours. Any name gets one of them, always
// the same
const colour = computed(() => {
  let sum = 0;
  for (const char of props.name) sum = (sum + (char.codePointAt(0) ?? 0)) % COLOURS.length;
  return COLOURS[sum] ?? { background: "", color: "" };
});
</script>

<template>
  <span class="mark" :class="{ plain: !logo }" :style="{ width: size + 'px', height: size + 'px' }">
    <img v-if="logo" :src="logo" alt="" class="logo" />
    <span
      v-else
      class="initial"
      :style="{ background: colour.background, color: colour.color, fontSize: size * 0.42 + 'px' }"
      aria-hidden="true"
    >
      {{ initial }}
    </span>
  </span>
</template>

<style scoped>
/* A square with soft corners; a thin border around a logo, none around
   the coloured initial, whose background is its own edge */
.mark {
  display: flex;
  flex: none;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  border: 1px solid var(--mt-border);
  border-radius: 10px;
  background: var(--mt-background);
}

.mark.plain {
  border-color: transparent;
}

.logo {
  width: 100%;
  height: 100%;
  padding: 8%;
  object-fit: contain;
}

.initial {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-weight: 600;
  line-height: 1;
}
</style>
