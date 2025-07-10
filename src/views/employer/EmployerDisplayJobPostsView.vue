<template>
  <div class="employer-job-posts">
    <ContentHeader
    title="Manage your job posts"
    description="View, edit, and delete your job offers."
    />
    <div class="header-container">
      <div class="header">
        <div class="title-section">
          <p class="stats" v-if="!loading && !error">
            <span class="job-count">{{ jobPosts.length }}</span>
            {{ jobPosts.length === 1 ? "job offer" : "job offers" }} published
          </p>
        </div>
        <button class="create-button" @click="$router.push('/employer/create-jobpost')">
          <i class="fas fa-plus-circle"></i> Create Job Offer
        </button>
      </div>
      <JobPostEditModal
        :show="showEditModal"
        @update:show="showEditModal = $event"
        :job-id="currentJobId"
        @job-updated="handleJobUpdated"
      />
    </div>
    <div class="content-container">
      <!-- Loading status -->
      <div v-if="loading" class="status-message loading">
        <i class="fas fa-spinner fa-spin"></i>
        <p>Loading your job posts...</p>
      </div>
      <!-- Error message -->
      <div v-if="error" class="status-message error">
        <i class="fas fa-exclamation-circle"></i>
        <p>{{ error }}</p>
        <button @click="fetchJobPosts" class="retry-button">
          <i class="fas fa-redo"></i> Try Again
        </button>
      </div>
      <!-- List of jobs -->
      <div v-if="!loading && !error" class="job-posts-list">
        <div v-if="jobPosts.length > 0">
          <JobPostCard v-for="jobPost in jobPosts" :key="jobPost.id" :job="jobPost">
            <!-- Using the slot to add action buttons -->
            <template #actions>
              <div class="action-buttons">
                <button class="edit-button" @click.stop="editJobPost(jobPost.id)">
                  <i class="fas fa-edit"></i> Edit
                </button>
                <button class="delete-button" @click.stop="confirmDelete(jobPost)">
                  <i class="fas fa-trash-alt"></i> Delete
                </button>
              </div>
            </template>
          </JobPostCard>
        </div>
        <!-- Message when no job is found -->
        <div v-else class="status-message empty">
          <i class="fas fa-briefcase"></i>
          <p>You haven't published any job offers yet.</p>
          <button class="create-button" @click="$router.push('/employer/create-jobpost')">
            <i class="fas fa-plus-circle"></i> Create Your First Job Offer
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api"
import JobPostCard from "@/components/JobPostCard.vue"
import JobPostEditModal from "@/components/JobPostEditModal.vue"
import ContentHeader from "@/components/ContentHeader.vue"

export default {
  name: "EmployerDisplayJobPostsView",
  components: {
    JobPostCard,
    JobPostEditModal,
    ContentHeader
  },
  data() {
    return {
      jobPosts: [],
      loading: true,
      error: null,
      showEditModal: false,
      currentJobId: null
    }
  },
  methods: {
    async fetchJobPosts() {
      this.loading = true
      this.error = null

      try {
        const response = await api.get("/employer-job-posts/")
        this.jobPosts = response.data
      } catch (err) {
        this.error = "Failed to load job posts. Please try again."
        console.error("Error fetching job posts:", err)
      } finally {
        this.loading = false
      }
    },

    editJobPost(jobId) {
      this.currentJobId = jobId
      this.showEditModal = true
    },

    handleJobUpdated() {
      this.fetchJobPosts()
    },

    confirmDelete(job) {
      if (confirm(`Are you sure you want to delete "${job.title}" job post?`)) {
        this.deleteJobPost(job.id)
      }
    },

    async deleteJobPost(jobId) {
      try {
        this.loading = true
        await api.delete(`/employer-job-posts/${jobId}/`)

        // Refresh the list after deletion
        this.jobPosts = this.jobPosts.filter((job) => job.id !== jobId)
      } catch (err) {
        this.error = "Failed to delete job post. Please try again."
        console.error("Error deleting job post:", err)
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    this.fetchJobPosts()
  }
}
</script>

<style scoped>
.employer-job-posts {
  width: 100%;
  min-height: 100%;
  background-color: #f8f9fa;
}

.header-container {
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
  padding: 20px 0;
  margin-bottom: 30px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 850px;
  margin: 0 auto;
  padding: 0 15px;
}

.title-section h1 {
  margin: 0;
  font-size: 2rem;
  color: #333;
  font-weight: 600;
}

.stats {
  margin: 5px 0 0 0;
  color: #666;
  font-size: 0.95rem;
}

.job-count {
  font-weight: 600;
  color: #044cd3;
}

.content-container {
  max-width: 880px;
  margin: 0 auto;
  padding: 0 15px;
}

.create-button {
  background-color: #4caf50;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 12px 20px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.create-button:hover {
  background-color: #45a049;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.create-button:active {
  transform: translateY(0);
}

.status-message {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  padding: 50px 20px;
  margin-top: 20px;
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 3px 10px rgba(0, 0, 0, 0.08);
}

.status-message i {
  font-size: 2rem;
  margin-bottom: 15px;
}

.status-message p {
  margin: 0 0 20px 0;
  font-size: 1.1rem;
  color: #555;
}

.loading i {
  color: #044cd3;
}

.error {
  color: #d32f2f;
}

.error i {
  color: #f44336;
}

.empty i {
  color: #666;
}

.retry-button {
  background-color: #f1f1f1;
  color: #333;
  border: none;
  border-radius: 6px;
  padding: 10px 18px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: background-color 0.2s;
}

.retry-button:hover {
  background-color: #e0e0e0;
}

/* Styles for action buttons */
.action-buttons {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  margin-top: 20px;
  margin-bottom: 20px;
}

.edit-button,
.delete-button {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: none;
  border-radius: 6px;
  font-size: 0.9rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.edit-button {
  background-color: #044cd3;
  color: white;
}

.edit-button:hover {
  background-color: #357ca5;
  transform: translateY(-2px);
}

.delete-button {
  background-color: #f44336;
  color: white;
}

.delete-button:hover {
  background-color: #d32f2f;
  transform: translateY(-2px);
}

@media (max-width: 768px) {
  .header {
    flex-direction: column;
    align-items: stretch;
    gap: 20px;
  }

  .title-section {
    text-align: center;
  }

  .create-button {
    width: 100%;
    justify-content: center;
  }

  .action-buttons {
    flex-direction: column;
    width: 100%;
  }

  .edit-button,
  .delete-button {
    width: 100%;
    justify-content: center;
  }
}
</style>
