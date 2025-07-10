<template>
  <div class="modal-overlay" v-if="show">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Edit Job Offer</h2>
        <button class="close-button" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <div v-if="loading" class="modal-loading">
          <i class="fas fa-spinner fa-spin"></i>
          <p>Loading job details...</p>
        </div>

        <div v-else-if="error" class="modal-error">
          <i class="fas fa-exclamation-circle"></i>
          <p>{{ error }}</p>
          <button @click="fetchJobDetails" class="retry-button">
            <i class="fas fa-redo"></i> Try Again
          </button>
        </div>

        <form v-else @submit.prevent="submitForm" class="job-edit-form">
          <div class="form-group">
            <label for="title">Job Title</label>
            <input type="text" id="title" v-model="formData.title" required placeholder="Enter job title" />
          </div>

          <div class="form-group">
            <label for="location">Location</label>
            <input type="text" id="location" v-model="formData.location" required placeholder="Enter job location" />
          </div>

          <div class="form-group">
            <label for="salary">Minmum salary</label>
            <input type="number" id="salary_min" v-model="formData.salary_min" placeholder="E.g., $50,000 - $70,000" />
          </div>

          <div class="form-group">
            <label for="salary">Maximum salary</label>
            <input type="number" id="salary_max" v-model="formData.salary_max" placeholder="E.g., $50,000 - $70,000" />
          </div>

          <div class="form-group">
            <label for="description">Job Description</label>
            <textarea id="description" v-model="formData.description" rows="6" required
              placeholder="Describe the job position, responsibilities, and requirements"></textarea>
          </div>

          <div class="form-group">
            <label for="salary">Year experience</label>
            <input type="number" id="years_experience" v-model="formData.years_experience" placeholder="2" />
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button class="cancel-button" @click="closeModal">Cancel</button>
        <button class="save-button" @click="submitForm" :disabled="submitting">
          <i v-if="submitting" class="fas fa-spinner fa-spin"></i>
          <span v-else>Save Changes</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api"

export default {
  name: "JobPostEditModal",
  props: {
    show: {
      type: Boolean,
      default: false
    },
    jobId: {
      type: [Number, String],
      default: null
    }
  },
  data() {
    return {
      loading: false,
      submitting: false,
      error: null,
      formData: {
        title: "",
        location: "",
        contract_type: "",
        salary: "",
        description: "",
        requirements: "",
        application_deadline: ""
      }
    }
  },
  watch: {
    jobId: {
      immediate: true,
      handler(newVal) {
        if (newVal && this.show) {
          this.fetchJobDetails()
        }
      }
    },
    show(newVal) {
      if (newVal && this.jobId) {
        this.fetchJobDetails()
      }
    }
  },
  methods: {
    async fetchJobDetails() {
      if (!this.jobId) return

      this.loading = true
      this.error = null

      try {
        const response = await api.get(`/employer-job-posts/${this.jobId}/`)
        this.formData = { ...response.data }

        if (this.formData.application_deadline) {
          const date = new Date(this.formData.application_deadline)
          this.formData.application_deadline = date.toISOString().split("T")[0]
        }
      } catch (err) {
        this.error = "Failed to load job details. Please try again."
        console.error("Error fetching job details:", err)
      } finally {
        this.loading = false
      }
    },

    async submitForm() {
      this.submitting = true

      try {
        await api.patch(`/employer-job-posts/${this.jobId}/`, this.formData)
        this.$emit("job-updated")
        this.closeModal()
      } catch (err) {
        this.error = "Failed to update job post. Please try again."
        console.error("Error updating job post:", err)
      } finally {
        this.submitting = false
      }
    },

    closeModal() {
      this.$emit("update:show", false)
      setTimeout(() => {
        this.error = null
        this.formData = {
          title: "",
          location: "",
          contract_type: "",
          salary: "",
          description: "",
          requirements: "",
          application_deadline: ""
        }
      }, 300)
    }
  }
}
</script>

<style scoped>
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
  z-index: 1000;
  padding: 20px;
}

.modal-container {
  background-color: white;
  border-radius: 12px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
  width: 100%;
  max-width: 650px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: modal-appear 0.3s ease;
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #eaeaea;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.5rem;
  color: #333;
  font-weight: 600;
}

.close-button {
  background: none;
  border: none;
  font-size: 1.2rem;
  color: #666;
  cursor: pointer;
  padding: 5px;
  transition: color 0.2s;
}

.close-button:hover {
  color: #333;
}

.modal-body {
  padding: 25px;
  overflow-y: auto;
}

.modal-loading,
.modal-error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 30px 0;
  text-align: center;
}

.modal-loading i,
.modal-error i {
  font-size: 2rem;
  margin-bottom: 15px;
}

.modal-loading i {
  color: #044cd3;
}

.modal-error i {
  color: #f44336;
}

.modal-loading p,
.modal-error p {
  margin: 0 0 20px 0;
  color: #555;
}

.job-edit-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-row {
  display: flex;
  gap: 20px;
}

.form-group.half {
  flex: 1;
}

label {
  font-weight: 500;
  color: #333;
  font-size: 0.95rem;
}

input,
select,
textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  transition: border-color 0.2s;
}

input:focus,
select:focus,
textarea:focus {
  border-color: #044cd3;
  outline: none;
}

textarea {
  resize: vertical;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 25px;
  border-top: 1px solid #eaeaea;
}

.cancel-button,
.save-button {
  padding: 12px 20px;
  border-radius: 6px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 120px;
}

.cancel-button {
  background-color: #f1f1f1;
  color: #333;
  border: none;
}

.cancel-button:hover {
  background-color: #e0e0e0;
}

.save-button {
  background-color: #044cd3;
  color: white;
  border: none;
}

.save-button:hover {
  background-color: #0041bb;
}

.save-button:disabled {
  background-color: #a6c8d8;
  cursor: not-allowed;
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

@media (max-width: 768px) {
  .form-row {
    flex-direction: column;
    gap: 20px;
  }

  .modal-container {
    max-height: 85vh;
    width: 95%;
  }

  .modal-header,
  .modal-body,
  .modal-footer {
    padding: 15px;
  }
}

@media (max-width: 768px) {

  input,
  select,
  textarea,
  .cancel-button,
  .save-button {
    width: 100%;
    box-sizing: border-box;
  }

  .modal-footer {
    flex-direction: column;
  }
}
</style>
