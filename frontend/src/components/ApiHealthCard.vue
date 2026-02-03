<script setup>
import { onMounted, ref } from "vue";

const props = defineProps({
  endpoint: { type: String, default: "/api/health/" },
  title: { type: String, default: "Backend status" },
});

const loading = ref(true);
const error = ref(null);
const status = ref(null);

async function check() {
  loading.value = true;
  error.value = null;

  try {
    const res = await fetch(props.endpoint, {
      headers: { Accept: "application/json" },
    });

    if (!res.ok) {
      throw new Error(`HTTP ${res.status}`);
    }

    const data = await res.json();
    status.value = data?.status ?? "unknown";
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(check);
</script>

<template>
  <section style="padding: 12px; border: 1px solid #ddd; border-radius: 8px;">
    <div style="display:flex; justify-content: space-between; align-items: center; gap: 12px;">
      <h2 style="margin: 0;">{{ title }}</h2>
      <button @click="check" :disabled="loading" style="padding: 6px 10px; cursor: pointer;">
        {{ loading ? "..." : "Refresh" }}
      </button>
    </div>

    <p v-if="loading" style="margin-top: 8px;">Checking API…</p>
    <p v-else-if="error" style="margin-top: 8px; color: #b00020;">API error: {{ error }}</p>
    <p v-else style="margin-top: 8px;">
      API: <strong>{{ status }}</strong>
    </p>
  </section>
</template>
