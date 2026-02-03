<script setup>
import { computed, onMounted, ref } from "vue";

const props = defineProps({
  // standard DRF endpoint (router): /api/messages/
  endpoint: { type: String, default: "/api/messages/" },
  title: { type: String, default: "Messages (CRUD)" },
});

const loading = ref(false);
const error = ref(null);
const items = ref([]);

const form = ref({
  subject: "",
  body: "",
});

const editingId = ref(null);
const editForm = ref({
  subject: "",
  body: "",
});

const canCreate = computed(() => form.value.subject.trim().length > 0);
const canSave = computed(() => editForm.value.subject.trim().length > 0);

async function apiFetch(url, options = {}) {
  const res = await fetch(url, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  // DRF sometimes returns error JSON -> we try to read it
  const text = await res.text();
  let payload = null;
  try {
    payload = text ? JSON.parse(text) : null;
  } catch {
    payload = text || null;
  }

  if (!res.ok) {
    // “clean” error message
    const detail =
      (payload && typeof payload === "object" && (payload.detail || payload.error)) ||
      (typeof payload === "string" ? payload : null) ||
      `HTTP ${res.status}`;
    throw new Error(detail);
  }

  return payload;
}

async function loadList() {
  loading.value = true;
  error.value = null;

  try {
    const data = await apiFetch(props.endpoint, { method: "GET" });

    // DRF: pagination if applicable {results: []} otherwise []
    items.value = Array.isArray(data) ? data : (data?.results ?? []);
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    loading.value = false;
  }
}

async function createItem() {
  if (!canCreate.value) return;

  loading.value = true;
  error.value = null;

  try {
    await apiFetch(props.endpoint, {
      method: "POST",
      body: JSON.stringify({
        subject: form.value.subject.trim(),
        body: form.value.body.trim(),
      }),
    });

    form.value.subject = "";
    form.value.body = "";

    await loadList();
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    loading.value = false;
  }
}

function startEdit(item) {
  editingId.value = item.id;
  editForm.value.subject = item.subject ?? "";
  editForm.value.body = item.body ?? "";
}

function cancelEdit() {
  editingId.value = null;
  editForm.value.subject = "";
  editForm.value.body = "";
}

async function saveEdit() {
  if (!editingId.value || !canSave.value) return;

  loading.value = true;
  error.value = null;

  try {
    // PATCH => partial update (more flexible)
    await apiFetch(`${props.endpoint}${editingId.value}/`, {
      method: "PATCH",
      body: JSON.stringify({
        subject: editForm.value.subject.trim(),
        body: editForm.value.body.trim(),
      }),
    });

    cancelEdit();
    await loadList();
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    loading.value = false;
  }
}

async function deleteItem(id) {
  if (!confirm("Delete this message?")) return;

  loading.value = true;
  error.value = null;

  try {
    await apiFetch(`${props.endpoint}${id}/`, { method: "DELETE" });
    await loadList();
  } catch (e) {
    error.value = e instanceof Error ? e.message : String(e);
  } finally {
    loading.value = false;
  }
}

onMounted(loadList);
</script>

<template>
  <section style="padding: 12px; border: 1px solid #ddd; border-radius: 8px; margin-top: 12px;">
    <div style="display:flex; justify-content: space-between; align-items: center; gap: 12px;">
      <h2 style="margin: 0;">{{ title }}</h2>
      <button @click="loadList" :disabled="loading" style="padding: 6px 10px; cursor: pointer;">
        {{ loading ? "..." : "Refresh" }}
      </button>
    </div>

    <p v-if="error" style="margin-top: 8px; color: #b00020;">Error: {{ error }}</p>

    <!-- Create -->
    <div style="margin-top: 12px; padding: 10px; border: 1px dashed #ccc; border-radius: 8px;">
      <h3 style="margin: 0 0 8px 0;">Create</h3>

      <div style="display:flex; gap: 8px; flex-wrap: wrap;">
        <input
          v-model="form.subject"
          placeholder="Subject (required)"
          style="padding: 8px; min-width: 240px; flex: 1;"
        />
        <button
          @click="createItem"
          :disabled="loading || !canCreate"
          style="padding: 8px 12px; cursor: pointer;"
        >
          Create
        </button>
      </div>

      <textarea
        v-model="form.body"
        placeholder="Body (optional)"
        rows="3"
        style="margin-top: 8px; padding: 8px; width: 100%;"
      />
    </div>

    <!-- List -->
    <div style="margin-top: 12px;">
      <h3 style="margin: 0 0 8px 0;">List</h3>

      <p v-if="loading && items.length === 0">Loading…</p>
      <p v-else-if="items.length === 0">No messages yet.</p>

      <ul v-else style="padding-left: 18px;">
        <li v-for="it in items" :key="it.id" style="margin-bottom: 10px;">
          <div style="display:flex; align-items: center; justify-content: space-between; gap: 10px;">
            <div>
              <strong>#{{ it.id }}</strong> — {{ it.subject }}
              <div style="font-size: 0.9em; opacity: 0.8; white-space: pre-wrap;">
                {{ it.body }}
              </div>
            </div>

            <div style="display:flex; gap: 8px;">
              <button @click="startEdit(it)" :disabled="loading" style="cursor: pointer;">Edit</button>
              <button @click="deleteItem(it.id)" :disabled="loading" style="cursor: pointer;">
                Delete
              </button>
            </div>
          </div>

          <!-- Edit -->
          <div
            v-if="editingId === it.id"
            style="margin-top: 8px; padding: 10px; background: rgba(0,0,0,0.05); border-radius: 8px;"
          >
            <div style="display:flex; gap: 8px; flex-wrap: wrap;">
              <input
                v-model="editForm.subject"
                placeholder="Subject (required)"
                style="padding: 8px; min-width: 240px; flex: 1;"
              />
              <button @click="saveEdit" :disabled="loading || !canSave" style="cursor: pointer;">
                Save
              </button>
              <button @click="cancelEdit" :disabled="loading" style="cursor: pointer;">Cancel</button>
            </div>

            <textarea
              v-model="editForm.body"
              placeholder="Body"
              rows="3"
              style="margin-top: 8px; padding: 8px; width: 100%;"
            />
          </div>
        </li>
      </ul>
    </div>
  </section>
</template>
