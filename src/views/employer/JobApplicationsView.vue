<template>
  <div class="p-6 min-h-screen bg-gray-50">
    <h1 class="text-3xl font-bold text-center mb-6 text-gray-800">
      Applications for Job #{{ jobId }}
    </h1>

    <div v-if="loading" class="text-center text-gray-500">Loading applications...</div>

    <div v-else-if="applications.length === 0" class="text-center text-gray-400">
      No applications received yet.
    </div>

    <div v-else class="space-y-6 max-w-4xl mx-auto">
      <div v-for="app in applications" :key="app.id" class="bg-white shadow-md border border-gray-200 rounded-lg p-6">
        <div class="flex justify-between items-center mb-2">
          <h2 class="text-xl font-semibold text-gray-700">👤 {{ app.candidate_username }}</h2>
          <span class="text-sm text-gray-500">
            {{ formatDate(app.applied_at) }}
          </span>
        </div>
        <p class="text-gray-600"><strong>💬 Cover letter:</strong> {{ app.cover_letter }}</p>
        <div v-if="app.cv_file" class="mt-3">
          📎 <a :href="app.cv_file" class="text-blue-600 underline" target="_blank">View CV</a>
        </div>
      </div>
    </div>

    <!-- Debug info -->
    <div v-if="debug" class="mt-10 p-4 bg-gray-100 text-sm rounded">
      <h3 class="font-bold mb-2">🔧 Debug Info</h3>
      <pre>{{ applications }}</pre>
    </div>
  </div>
</template>

<script>
import api from "@/services/api"

export default {
  name: "JobApplicationsView",
  data() {
    return {
      applications: [],
      loading: true,
      debug: false, // Enable debugging if necessary
      jobId: this.$route.params.id
    }
  },
  methods: {
    async fetchApplications() {
      try {
        const response = await api.get(`/jobposts/${this.jobId}/applications/`)
        this.applications = response.data
      } catch (error) {
        console.error("Failed to fetch applications:", error)
      } finally {
        this.loading = false
      }
    },
    formatDate(dateStr) {
      const date = new Date(dateStr)
      return date.toLocaleDateString("en-GB", {
        year: "numeric",
        month: "short",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit"
      })
    }
  },
  created() {
    this.fetchApplications()
  }
}
</script>

<style scoped>
a {
  font-weight: 500;
}
</style>
