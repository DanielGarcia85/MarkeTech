<template>
  <div>
    <ContentHeader title="Check your job applications" description="View and manage your job applications." />
    <div class="premium-status-banner" v-if="userPremiumStatus && userPremiumStatus.isPremium">
      <div class="premium-info">
        <PremiumBadge :isPremium="true" variant="large" />
        <span class="premium-text">
          Your applications are prioritized and appear first to employers!
        </span>
      </div>
    </div>
    <div class="jobseeker-applications-view">
      <h1 class="page-title">My Applications</h1>

      <div v-if="loading" class="loading-container">
        <div class="loading-spinner"></div>
        <p>Loading your applications...</p>
      </div>

      <div v-else-if="applications.length === 0" class="empty-state">
        <h2>No applications yet</h2>
        <p>You haven't applied to any jobs yet. Start exploring opportunities!</p>
        <router-link to="/" class="browse-jobs-btn">Browse Jobs</router-link>
      </div>

      <div v-else class="applications-grid">
        <div v-for="application in applications" :key="application.id" class="application-card">
          <div class="application-header">
            <h2 class="job-title">{{ application.job_title }}</h2>
            <div :class="['status-badge', getStatusClass(application.status)]">
              {{ getStatusLabel(application.status) }}
            </div>
          </div>

          <div class="application-info">
            <div class="info-row">
              <i class="fas fa-building"></i>
              <span>{{ application.job_company }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-map-marker-alt"></i>
              <span> {{ application.job_location }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-calendar-alt"></i>
              <span>Applied on {{ formatDate(application.applied_at) }}</span>
            </div>
            <div v-if="application.status !== 'received' && application.status_updated_at"
              class="info-row status-update">
              <i class="fas fa-clock"></i>
              <span>Status updated on {{ formatDate(application.status_updated_at) }}</span>
            </div>
          </div>

          <div class="application-actions">
            <button @click="viewDetails(application)" class="details-btn">View Details</button>
            <button @click="messageEmployer(application)" class="details-btn">
              Contact Employer
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="selectedApplication" class="modal">
      <div class="modal-content">
        <span class="close-modal" @click="selectedApplication = null">&times;</span>
        <h2 class="modal-title">Application Details</h2>

        <div class="application-details">
          <div class="status-banner" :class="getStatusClass(selectedApplication.status)">
            <div class="status-icon">
              <i :class="getStatusIcon(selectedApplication.status)"></i>
            </div>
            <div class="status-text">
              <span class="status-label">Status:</span>
              <span class="status-value">{{ getStatusLabel(selectedApplication.status) }}</span>
              <span v-if="selectedApplication.status !== 'received'" class="status-date">
                Updated on {{ formatDate(selectedApplication.status_updated_at) }}
              </span>
            </div>
          </div>

          <div class="application-info">
            <div class="info-row">
              <i class="fas fa-building"></i>
              <span>{{ selectedApplication.job_company }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-map-marker-alt"></i>
              <span>{{ selectedApplication.job_location }}</span>
            </div>
            <div class="info-row">
              <i class="fas fa-calendar-alt"></i>
              <span>Applied on {{ formatDate(selectedApplication.applied_at) }}</span>
            </div>
          </div>

          <div class="application-actions">
            <button @click="viewDetails(selectedApplication)" class="details-btn">
              <i class="fas fa-eye"></i> View Details
            </button>
            <button @click="messageEmployer(selectedApplication)" class="message-btn">
              <i class="fas fa-comment"></i> Contact Employer
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- Application details modal -->
    <div v-if="selectedApplication" class="modal-overlay" @click="closeModal">
      <div class="modal-container" @click.stop>
        <div class="modal-header">
          <h2>Application Details</h2>
          <button class="close-button" @click="closeModal">
            <i class="fas fa-times"></i>
          </button>
        </div>
        <div class="modal-body">
          <!-- Status banner -->
          <div class="status-banner" :class="getStatusClass(selectedApplication.status)">
            <div class="status-icon">
              <i :class="getStatusIcon(selectedApplication.status)"></i>
            </div>
            <div class="status-text">
              <span class="status-label">Status</span>
              <span class="status-value">{{ getStatusLabel(selectedApplication.status) }}</span>
            </div>
          </div>

          <!-- Job information -->
          <div class="detail-section">
            <h3>Job Information</h3>
            <div class="detail-grid">
              <div class="detail-item">
                <div class="detail-label">Position</div>
                <div class="detail-value">{{ selectedApplication.job_title }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Company</div>
                <div class="detail-value">{{ selectedApplication.job_company }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Location</div>
                <div class="detail-value">{{ selectedApplication.job_location }}</div>
              </div>
              <div class="detail-item">
                <div class="detail-label">Applied on</div>
                <div class="detail-value">{{ formatDate(selectedApplication.applied_at) }}</div>
              </div>
            </div>
          </div>

          <!-- Documents -->
          <div class="detail-section">
            <h3>Your Documents</h3>
            <div class="documents-grid">
              <a v-if="selectedApplication.cv_file" :href="selectedApplication.cv_file" target="_blank"
                class="document-link">
                <i class="fas fa-file-pdf"></i>
                <span>View Your CV</span>
              </a>
              <a v-if="selectedApplication.cover_letter_file" :href="selectedApplication.cover_letter_file"
                target="_blank" class="document-link">
                <i class="fas fa-file-alt"></i>
                <span>View Cover Letter</span>
              </a>
            </div>
          </div>

          <!-- Application timeline -->
          <div class="timeline">
            <div class="timeline-item completed">
              <div class="timeline-marker">
                <i class="fas fa-paper-plane"></i>
              </div>
              <div class="timeline-content">
                <h4>Application Submitted</h4>
                <p>{{ formatDate(getStatusUpdateDate('received')) }}</p>
              </div>
            </div>

            <div class="timeline-item"
              :class="{ completed: isStepCompleted('in_progress', selectedApplication.status) }">
              <div class="timeline-marker">
                <i class="fas fa-search"></i>
              </div>
              <div class="timeline-content">
                <h4>Application in Review</h4>
                <p v-if="isStepCompleted('in_progress', selectedApplication.status)">
                  Your application is being reviewed {{ formatDate(getStatusUpdateDate('in_progress')) }}
                </p>
                <p v-else>Waiting</p>
              </div>
            </div>

            <div class="timeline-item" :class="{
              completed: isStepCompleted('accepted', selectedApplication.status),
              rejected: selectedApplication.status === 'rejected'
            }">
              <div class="timeline-marker">
                <i :class="{
                  'fas fa-check-circle': selectedApplication.status === 'accepted',
                  'fas fa-times-circle': selectedApplication.status === 'rejected',
                  'fas fa-clock': !['accepted', 'rejected'].includes(selectedApplication.status)
                }"></i>
              </div>
              <div class="timeline-content">
                <h4 v-if="selectedApplication.status === 'accepted'">Application Accepted</h4>
                <h4 v-else-if="selectedApplication.status === 'rejected'">Application Rejected</h4>
                <h4 v-else>Final Decision</h4>
                <p v-if="selectedApplication.status === 'accepted'">
                  Congratulations! {{ formatDate(getStatusUpdateDate('accepted')) }}
                </p>
                <p v-else-if="selectedApplication.status === 'rejected'">
                  Keep trying! {{ formatDate(getStatusUpdateDate('rejected')) }}
                </p>
                <p v-else>Pending</p>
              </div>
            </div>
          </div>


          <div class="modal-footer">
            <button @click="messageEmployer(selectedApplication)" class="message-btn">
              <i class="fas fa-comment"></i> Contact Employer
            </button>
            <button @click="closeModal" class="close-btn">Close</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import applicationService from "@/services/applicationService"
import ContentHeader from "@/components/ContentHeader.vue"
import PremiumBadge from "@/components/PremiumBadge.vue"
import premiumService from "@/services/premiumService"

export default {
  name: "JobSeekerApplicationsView",
  components: {
    ContentHeader,
    PremiumBadge
  },
  data() {
    return {
      applications: [],
      loading: true,
      selectedApplication: null,
      statusHistory: {},
      userPremiumStatus: null
    }
  },
  methods: {
    async fetchApplications() {
      try {
        this.loading = true
        const applications = await applicationService.getJobSeekerApplications()
        this.applications = applications
      } catch (error) {
        console.error("Failed to load applications:", error)
      } finally {
        this.loading = false
      }
    },

    formatDate(dateString) {
      if (!dateString) return "N/A"

      const date = new Date(dateString)
      return date.toLocaleDateString("en-GB", {
        year: "numeric",
        month: "long",
        day: "numeric",
        hour: "2-digit",
        minute: "2-digit"
      })
    },
    async fetchUserPremiumStatus() {
      try {
        const status = await premiumService.getPremiumStatus()

        this.userPremiumStatus = {
          isPremium: status.is_premium === true,
          userType: status.user_type
        }
      } catch (error) {
        console.error("Failed to fetch premium status:", error)
      }
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
    },

    getStatusLabel(status) {
      switch (status) {
        case "received":
          return "Received"
        case "in_progress":
          return "In Progress"
        case "accepted":
          return "Accepted"
        case "rejected":
          return "Rejected"
        default:
          return "Unknown"
      }
    },

    getStatusIcon(status) {
      switch (status) {
        case "received":
          return "fas fa-envelope"
        case "in_progress":
          return "fas fa-search"
        case "accepted":
          return "fas fa-check-circle"
        case "rejected":
          return "fas fa-times-circle"
        default:
          return "fas fa-question-circle"
      }
    },

    isStepCompleted(step, currentStatus) {
      const steps = ["received", "in_progress", "accepted"]
      const currentIndex = steps.indexOf(currentStatus)
      const stepIndex = steps.indexOf(step)
      return stepIndex <= currentIndex
    },

    viewDetails(application) {
      this.selectedApplication = application
      document.body.style.overflow = 'hidden'
      this.buildStatusHistory(application)
    },

    closeModal() {
      const app = this.selectedApplication
      this.selectedApplication = null
      document.body.style.overflow = ''
      if (app) {
        this.buildStatusHistory(app)
      }
    },

    buildStatusHistory(application) {
      if (!application) return;

      this.statusHistory = {}

      const steps = ["received", "in_progress", "accepted", "rejected"]
      const currentStatusIndex = steps.indexOf(application.status)

      this.statusHistory.received = application.applied_at

      if (currentStatusIndex >= 1) {
        this.statusHistory.in_progress = application.status_updated_at
      }

      if (currentStatusIndex >= 2) {
        this.statusHistory[application.status] = application.status_updated_at
      }
    },

    getStatusUpdateDate(status) {
      return this.statusHistory[status] || null
    },

    async messageEmployer(application) {
      try {
        const { id } = await applicationService.startConversation(application.id)
        this.$router.push({ path: "/messages", query: { conversation: id } })
      } catch (error) {
        console.error("Error starting conversation:", error)
      }
    }
  },
  async created() {
    this.fetchApplications(),
      await this.fetchUserPremiumStatus()
  },
  beforeDestroy() {
    // Ensure body scrolling is restored when component is destroyed
    document.body.style.overflow = ''
  }
}
</script>

<style scoped>
.premium-status-banner {
  background: linear-gradient(135deg, #fff8e1, #fff3c4);
  border: 1px solid #ffd54f;
  border-radius: 8px;
  padding: 1rem;
  margin: 1rem auto;
  max-width: 800px;
}

.premium-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  justify-content: center;
}

.premium-text {
  color: #f57f17;
  font-weight: 500;
}

.jobseeker-applications-view {
  padding: 1.5rem;
  min-height: calc(100vh - 200px);
  background-color: #f9fafb;
}

/* Loading state */
.loading-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 0;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 4px solid rgba(0, 0, 0, 0.1);
  border-radius: 50%;
  border-top-color: #044cd3;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }

  100% {
    transform: rotate(360deg);
  }
}

/* Empty state */
.empty-state {
  text-align: center;
  padding: 3rem 1.5rem;
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
  max-width: 600px;
}

.empty-state h2 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #374151;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 2rem;
}

.browse-jobs-btn {
  display: inline-block;
  background-color: #044cd3;
  color: white;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  text-decoration: none;
  font-weight: 500;
  transition: background-color 0.2s;
}

.browse-jobs-btn:hover {
  background-color: #0341b9;
}

/* Applications grid */
.applications-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 1.5rem;
}

@media (max-width: 768px) {
  .applications-grid {
    grid-template-columns: 1fr;
  }

  .jobseeker-applications-view {
    padding: 1rem;
  }
}

/* Application card */
.application-card {
  background-color: white;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  transition: transform 0.2s, box-shadow 0.2s;
  display: flex;
  flex-direction: column;
}

.application-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.application-header {
  padding: 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.job-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #111827;
  margin: 0;
  flex: 1;
  margin-right: 1rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  white-space: nowrap;
}

.application-info {
  padding: 1.25rem;
  flex: 1;
}

.info-row {
  display: flex;
  align-items: center;
  margin-bottom: 0.75rem;
  color: #4b5563;
}

.info-row i {
  width: 1.25rem;
  margin-right: 0.75rem;
  color: #6b7280;
}

.application-actions {
  padding: 1.25rem;
  border-top: 1px solid #e5e7eb;
  background-color: #f9fafb;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.details-btn,
.message-btn {
  width: 100%;
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.details-btn {
  background-color: #044cd3;
  color: white;
}

.details-btn:hover {
  background-color: #0341b9;
}

.message-btn {
  background-color: #1e40af;
  color: white;
}

.message-btn:hover {
  background-color: #1e3a8a;
}

/* Modal styles */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
  padding: 1rem;
  overflow-y: auto;
}

.modal-container {
  background-color: white;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 700px;
  max-height: 90vh;
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  animation: modal-appear 0.3s ease-out;
  position: relative;
  z-index: 10000;
}

@keyframes modal-appear {
  from {
    opacity: 0;
    transform: translateY(20px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.modal-header {
  padding: 1.25rem;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  background-color: white;
  z-index: 1;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #111827;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.25rem;
  color: #6b7280;
  cursor: pointer;
  padding: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 9999px;
  transition: background-color 0.2s;
}

.close-button:hover {
  background-color: #f3f4f6;
  color: #111827;
}

.modal-body {
  padding: 1.5rem;
  flex: 1;
  overflow-y: auto;
}

.modal-footer {
  padding: 1.25rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  background-color: #f9fafb;
}

@media (max-width: 640px) {
  .modal-footer {
    flex-direction: column;
  }

  .modal-footer button {
    width: 100%;
  }
}

.close-btn {
  padding: 0.5rem 1.25rem;
  background-color: #e5e7eb;
  color: #374151;
  border: none;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.close-btn:hover {
  background-color: #d1d5db;
}

/* Status banner */
.status-banner {
  display: flex;
  align-items: center;
  padding: 1rem;
  margin-bottom: 1.5rem;
  border-radius: 0.5rem;
}

.status-icon {
  font-size: 1.75rem;
  margin-right: 1rem;
}

.status-text {
  display: flex;
  flex-direction: column;
}

.status-label {
  font-size: 0.875rem;
  font-weight: 500;
}

.status-value {
  font-size: 1.125rem;
  font-weight: 600;
}

.status-date {
  font-size: 0.875rem;
  margin-top: 0.25rem;
  font-style: italic;
}

.detail-section {
  margin-bottom: 2rem;
}

.detail-section h3 {
  font-size: 1.125rem;
  margin-bottom: 1rem;
  color: #374151;
  font-weight: 600;
  position: relative;
  padding-bottom: 0.5rem;
}

.detail-section h3::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 3rem;
  height: 2px;
  background-color: #044cd3;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  gap: 1rem;
}

@media (max-width: 640px) {
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

.detail-item {
  margin-bottom: 0.75rem;
}

.detail-label {
  font-weight: 500;
  color: #6b7280;
  margin-bottom: 0.25rem;
}

.detail-value {
  color: #111827;
}

.documents-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.status-update {
  font-style: italic;
  color: #6b7280;
  background-color: #f3f4f6;
  padding: 0.5rem;
  border-radius: 0.25rem;
  margin-top: 0.5rem;
}

.cover-letter {
  background-color: #f9fafb;
  padding: 1rem;
  border-radius: 0.5rem;
  white-space: pre-line;
  color: #374151;
  line-height: 1.6;
}

.document-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #f3f4f6;
  border-radius: 0.5rem;
  color: #044cd3;
  text-decoration: none;
  transition: background-color 0.2s;
}

.document-link:hover {
  background-color: #e5e7eb;
}

/* Timeline */
.timeline {
  position: relative;
  padding-left: 2.5rem;
}

.timeline::before {
  content: '';
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0.75rem;
  width: 2px;
  background-color: #e5e7eb;
}

.timeline-item {
  position: relative;
  padding-bottom: 2rem;
}

.timeline-item:last-child {
  padding-bottom: 0;
}

.timeline-marker {
  position: absolute;
  top: 0;
  left: -2.5rem;
  width: 1.5rem;
  height: 1.5rem;
  background-color: #f3f4f6;
  border: 2px solid #e5e7eb;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  color: #9ca3af;
  z-index: 1;
}

.timeline-item.completed .timeline-marker {
  background-color: #d1fae5;
  border-color: #10b981;
  color: #059669;
}

.timeline-item.rejected .timeline-marker {
  background-color: #fee2e2;
  border-color: #ef4444;
  color: #dc2626;
}

.timeline-content {
  padding-left: 0.5rem;
}

.timeline-content h4 {
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.5rem 0;
  color: #111827;
}

.timeline-content p {
  color: #6b7280;
  margin: 0;
}

/* Status Colors */
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
  .status-banner {
    flex-direction: column;
    text-align: center;
    padding: 1.5rem 1rem;
  }

  .status-icon {
    margin-right: 0;
    margin-bottom: 0.75rem;
    font-size: 2rem;
  }

  .detail-section h3::after {
    left: 50%;
    transform: translateX(-50%);
    width: 4rem;
  }

  .detail-section h3 {
    text-align: center;
  }
}
</style>
