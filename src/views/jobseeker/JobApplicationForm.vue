<!-- src/components/JobApplicationForm.vue -->
<template>
  <div class="modal-overlay" v-if="show" @click.self="closeModal">
    <div class="modal-container">
      <div class="modal-header">
        <h2>Apply for {{ job.title }}</h2>
        <button class="close-button" @click="closeModal">
          <i class="fas fa-times"></i>
        </button>
      </div>

      <div class="modal-body">
        <form @submit.prevent="submitApplication" class="application-form">
          <!-- Cover Letter -->
          <div class="form-group">
            <label for="coverLetter">Cover Letter (PDF)</label>
            <div class="file-input-container">
              <input
                type="file"
                id="coverLetter"
                ref="coverLetterInput"
                @change="handleCoverLetterUpload"
                accept="application/pdf"
              />
              <div class="file-input-display">
                <span v-if="formData.coverLetterFile">{{ formData.coverLetterFile.name }}</span>
                <span v-else>No file selected</span>
                <button type="button" @click="triggerCoverLetterInput" class="browse-button">
                  Browse
                </button>
              </div>
            </div>
            <div class="file-format-hint">Accepted format: PDF only. Maximum size: 5MB</div>
          </div>

          <div class="form-group">
            <label for="cv">Resume/CV</label>
            <div class="file-input-container">
              <input
                type="file"
                id="cv"
                ref="cvfileInput"
                @change="handleFileUpload"
                accept=".pdf,.doc,.docx"
              />
              <div class="file-input-display">
                <span v-if="cvFile">{{ cvFile.name }}</span>
                <span v-else>No file selected</span>
                <button type="button" @click="triggerFileInput" class="browse-button">
                  Browse
                </button>
              </div>
            </div>
            <div class="file-format-hint">Accepted formats: PDF, DOC, DOCX. Maximum size: 5MB</div>
          </div>

          <div v-if="errorMessage" class="error-message">
            {{ errorMessage }}
          </div>
        </form>
      </div>

      <div class="modal-footer">
        <button class="cancel-button" @click="closeModal">Cancel</button>
        <button
          class="submit-button"
          @click="submitApplication"
          :disabled="isSubmitting || coverLetterLength > 1000"
        >
          <i v-if="isSubmitting" class="fas fa-spinner fa-spin"></i>
          <span v-else>Submit Application</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script>
import applicationService from "@/services/applicationService"

export default {
  name: "JobApplicationForm",
  props: {
    show: {
      type: Boolean,
      default: false
    },
    job: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      formData: {
        coverLetterFile: null
      },
      cvFile: null,
      isSubmitting: false,
      errorMessage: ""
    }
  },
  methods: {
    closeModal() {
      this.$emit("close")
      this.formData.coverLetterFile = null
      this.cvFile = null
      this.errorMessage = ""
      this.$refs.coverLetterInput.value = ""
      this.$refs.cvfileInput.value = ""
    },
    handleCoverLetterUpload(event) {
      const file = event.target.files[0]
      if (file) {
        if (file.type !== "application/pdf") {
          this.errorMessage = "Please upload a PDF file for the cover letter"
          this.formData.coverLetterFile = null
          this.$refs.coverLetterInput.value = ""
          return
        }

        const maxSize = 5 * 1024 * 1024
        if (file.size > maxSize) {
          this.errorMessage = "Cover letter PDF should not exceed 5MB"
          this.formData.coverLetterFile = null
          this.$refs.coverLetterInput.value = ""
          return
        }

        this.formData.coverLetterFile = file
        this.errorMessage = ""
      }
    },
    handleFileUpload(event) {
      const file = event.target.files[0]
      if (file) {
        const validTypes = [
          "application/pdf",
          "application/msword",
          "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        ]
        if (!validTypes.includes(file.type)) {
          this.errorMessage = "Please upload a PDF or Word document for the CV"
          this.cvFile = null
          this.$refs.cvfileInput.value = ""
          return
        }

        const maxSize = 5 * 1024 * 1024
        if (file.size > maxSize) {
          this.errorMessage = "CV file size should not exceed 5MB"
          this.cvFile = null
          this.$refs.cvfileInput.value = ""
          return
        }

        this.cvFile = file
        this.errorMessage = ""
      }
    },
    triggerCoverLetterInput() {
      this.$refs.coverLetterInput.click()
    },
    triggerFileInput() {
      this.$refs.cvfileInput.click()
    },
    async submitApplication() {
      if (!this.formData.coverLetterFile) {
        this.errorMessage = "Please upload your cover letter in PDF format"
        return
      }

      this.isSubmitting = true
      this.errorMessage = ""

      try {
        const formData = new FormData()
        formData.append("cover_letter_file", this.formData.coverLetterFile)
        if (this.cvFile) {
          formData.append("cv_file", this.cvFile)
        }

        await applicationService.submitApplication(this.job.id, formData)

        this.$emit("submitted")
        this.closeModal()
      } catch (error) {
        if (error.response && error.response.data) {
          this.errorMessage = error.response.data.error || "Failed to submit application"
        } else {
          this.errorMessage = "An error occurred while submitting your application"
        }
        console.error("Application submission error:", error)
      } finally {
        this.isSubmitting = false
      }
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
  flex: 1;
}

.application-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

label {
  font-weight: 500;
  color: #333;
  font-size: 0.95rem;
}

textarea {
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 1rem;
  font-family: inherit;
  transition: border-color 0.2s;
  resize: vertical;
}

textarea:focus {
  border-color: #044cd3;
  outline: none;
}

.text-counter {
  font-size: 0.85rem;
  color: #777;
  text-align: right;
}

.text-danger {
  color: #e53e3e;
}

.file-input-container {
  position: relative;
}

.file-input-container input[type="file"] {
  position: absolute;
  top: 0;
  left: 0;
  opacity: 0;
  width: 0.1px;
  height: 0.1px;
  overflow: hidden;
}

.file-input-display {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  background-color: #f9fafb;
  box-sizing: border-box;
}

.browse-button {
  background-color: #e5e7eb;
  color: #374151;
  border: none;
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.9rem;
  cursor: pointer;
  transition: background-color 0.2s;
  box-sizing: border-box;
  flex-shrink: 0;
  margin-left: 10px;
}

.browse-button:hover {
  background-color: #d1d5db;
}

.file-format-hint {
  font-size: 0.8rem;
  color: #777;
  margin-top: 5px;
}

.error-message {
  background-color: #fee2e2;
  color: #b91c1c;
  padding: 12px;
  border-radius: 6px;
  margin-top: 10px;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 15px;
  padding: 20px 25px;
  border-top: 1px solid #eaeaea;
}

.cancel-button,
.submit-button {
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
  box-sizing: border-box;
}

.cancel-button {
  background-color: #f1f1f1;
  color: #333;
  border: none;
}

.cancel-button:hover {
  background-color: #e0e0e0;
}

.submit-button {
  background-color: #044cd3;
  color: white;
  border: none;
}

.submit-button:hover {
  background-color: #0341b9;
}

.submit-button:disabled {
  background-color: #a6c8d8;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .modal-container {
    max-height: 85vh;
    width: 95%;
  }

  .modal-header, .modal-body, .modal-footer {
    padding: 15px;
  }

  .modal-footer {
    flex-direction: column;
    gap: 10px;
  }

  .cancel-button, .submit-button {
    width: 100%;
  }

  .file-input-display {
    flex-direction: column;
    align-items: flex-start;
  }

  .browse-button {
    margin-top: 10px;
    margin-left: 0;
    width: 100%;
  }
}

@media (max-width: 768px) {
  .file-input-display {
    width: 100%;
    box-sizing: border-box;
  }

  .browse-button {
    box-sizing: border-box;
  }
}
</style>
