<template>
  <div>
    <ContentHeader title="Manage your job applications"
      description="View and manage the applications for your job posts." />
    <div class="applications-container">
      <div v-if="loading" class="text-center">Loading...</div>
      <div v-else-if="jobPosts.length === 0" class="text-center">No job posts available.</div>
      <div v-else class="job-list">
        <div v-for="job in jobPosts" :key="job.id" class="job-card">
          <div class="job-header">
            <div class="job-title-container">
              <button @click="toggle(job.id)" class="toggle-btn">
                <span v-if="open.includes(job.id)">▼</span>
                <span v-else>▶</span>
              </button>
              <h2 class="job-title">{{ job.title }} – {{ job.location }}</h2>
            </div>
          </div>

          <!-- Applications table moved inside the job loop -->
          <div v-if="open.includes(job.id)" class="applications-table-container">
            <table class="applications-table">
              <thead>
                <tr>
                  <th>Name of Candidate</th>
                  <th>CV</th>
                  <th>Application date</th>
                  <th>Status</th>
                  <th>Status updated</th>
                  <th>Contact</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="app in applications[job.id]" :key="app.id">
                  <td>
                    <div class="candidate-name-container">
                      {{ app.candidate_name }}
                      <PremiumBadge :isPremium="app.is_candidate_premium" variant="small" label="Premium Candidate" />
                    </div>
                  </td>
                  <td>
                    <a v-if="app.cv_file" :href="app.cv_file" target="_blank" class="cv-link">See CV</a>
                    <span v-else class="no-cv">No CV</span>
                  </td>
                  <td>{{ formatDate(app.applied_at) }}</td>
                  <td>
                    <select v-model="app.status" class="status-select" :class="getStatusClass(app.status)"
                      @change="updateStatus(app.id, app.status)" :disabled="updateStatusLoading[app.id]">
                      <option value="received">Received</option>
                      <option value="in_progress">In Progress</option>
                      <option value="accepted">Accepted</option>
                      <option value="rejected">Rejected</option>
                    </select>
                  </td>
                  <td>
                    <span v-if="app.status_updated_at" class="status-date">
                      {{ formatDateTime(app.status_updated_at) }}
                    </span>
                    <span v-else>-</span>
                  </td>
                  <td>
                    <router-link :to="{ name: 'messages', query: { application_id: app.id } }" class="message-link">
                      Message
                    </router-link>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api"
import applicationService from "@/services/applicationService"
import ContentHeader from "@/components/ContentHeader.vue"
import PremiumBadge from "@/components/PremiumBadge.vue"

export default {
  name: "EmployerApplicationsOverview",
  components: {
    ContentHeader,
    PremiumBadge
  },
  data() {
    return {
      loading: true,
      jobPosts: [],
      applications: {},
      loadingApplications: {},
      open: [],
      selectedApplication: null,
      updateStatusLoading: {}
    }
  },
  methods: {
    async fetchApplications(jobId) {
      try {
        const res = await api.get(`/jobposts/${jobId}/applications/`)
        this.applications = {
          ...this.applications,
          [jobId]: res.data
        }
      } catch (error) {
        console.error(`Erreur lors du chargement des candidatures pour le job ${jobId}:`, error)
      }
    },
    async fetchJobs() {
      try {
        const res = await api.get("/employer-job-posts/")
        this.jobPosts = res.data
        for (const job of res.data) {
          this.applications[job.id] = []
        }
      } catch (err) {
        console.error(err)
      } finally {
        this.loading = false
      }
    },
    async toggle(jobId) {
      if (this.open.includes(jobId)) {
        this.open = this.open.filter((id) => id !== jobId)
      } else {
        this.open.push(jobId)
        if (this.applications[jobId].length === 0) {
          const res = await api.get(`/jobposts/${jobId}/applications/`, {
            withCredentials: true
          })
          this.applications[jobId] = res.data
        }
      }
    },
    formatDate(date) {
      return new Date(date).toLocaleDateString("fr-CH")
    },
    formatDateTime(date) {
      if (!date) return "-"
      const dateObj = new Date(date)

      return (
        dateObj.toLocaleDateString("fr-CH") +
        " " +
        dateObj.toLocaleTimeString("fr-CH", {
          hour: "2-digit",
          minute: "2-digit"
        })
      )
    },
    async updateStatus(applicationId, newStatus) {
      if (!this.updateStatusLoading) {
        this.updateStatusLoading = {}
      }
      this.updateStatusLoading[applicationId] = true

      try {
        await applicationService.updateApplicationStatus(applicationId, newStatus)
        const jobId = this.findJobIdForApplication(applicationId)
        if (jobId) {
          await this.fetchApplications(jobId)
        }

        if (this.selectedApplication && this.selectedApplication.id === applicationId) {
          this.selectedApplication.status = newStatus
        }
      } catch (error) {
        console.error("Failed to update application status:", error)
      } finally {
        this.updateStatusLoading[applicationId] = false
      }
    },

    findJobIdForApplication(applicationId) {
      for (const jobId in this.applications) {
        if (this.applications[jobId].some((app) => app.id === applicationId)) {
          return jobId
        }
      }
      return null
    },
    getStatusClass(status) {
      switch (status) {
        case "received":
          return "status-received"
        case "in_progress":
          return "status-in-progress"
        case "accepted":
          return "status-accepted"
        case "rejected":
          return "status-rejected"
        default:
          return ""
      }
    }
  },
  async mounted() {
    await this.fetchJobs()
  }
}
</script>

<style scoped>
.candidate-name-container {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.applications-container {
  padding: 2rem;
  background-color: #ffffff;
  min-height: 100%;
  font-family: Arial, sans-serif;
  color: #1f2937;
}

.page-title {
  font-size: 2rem;
  font-weight: bold;
  margin-bottom: 2rem;
}

.text-center {
  text-align: center;
  color: #6b7280;
  font-size: 1rem;
}

.job-list {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.job-card {
  border: 1px solid #e5e7eb;
  border-radius: 1rem;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.job-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #e5e7eb;
  background-color: #f9fafb;
  border-top-left-radius: 1rem;
  border-top-right-radius: 1rem;
}

.job-title-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.toggle-btn {
  width: 2rem;
  height: 2rem;
  border: 1px solid #d1d5db;
  border-radius: 9999px;
  display: flex;
  justify-content: center;
  align-items: center;
  background: white;
  cursor: pointer;
}

.job-title {
  font-size: 1.125rem;
  font-weight: 600;
}

.applications-table-container {
  padding: 1.5rem;
  overflow-x: auto;
}

.applications-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.applications-table th {
  text-align: left;
  padding: 0.75rem 0.5rem;
  color: #2563eb;
  border-bottom: 1px solid #d1d5db;
}

.applications-table td {
  padding: 0.75rem 0.5rem;
  border-top: 1px solid #e5e7eb;
}

.applications-table tr:hover {
  background-color: #f3f4f6;
}

.cv-link {
  color: #2563eb;
  text-decoration: none;
}

.cv-link:hover {
  text-decoration: underline;
}

.no-cv {
  font-style: italic;
  color: #9ca3af;
}

.status-select {
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
  background-color: white;
}

.message-link {
  color: #2563eb;
  text-decoration: none;
}

.message-link:hover {
  text-decoration: underline;
}

.status-date {
  font-size: 0.8rem;
  color: #6b7280;
  white-space: nowrap;
}

.status-received {
  background-color: #e5e7eb;
  color: #374151;
}

.status-in-progress {
  background-color: #dbeafe;
  color: #1e40af;
}

.status-accepted {
  background-color: #d1fae5;
  color: #065f46;
}

.status-rejected {
  background-color: #fee2e2;
  color: #b91c1c;
}

@media (max-width: 768px) {
  .applications-container {
    padding: 1rem;
  }

  .applications-table-container {
    overflow-x: auto;
  }

  .applications-table {
    min-width: 650px;
  }
}
</style>
