<template>
  <div>
    <ContentHeader
    title="Change your profile"
    description="Update your job seeker profile information."
    />
     <div class="premium-section-container">
      <PremiumToggle />
    </div>
    <div class="profil-page">
      <div class="profil-card">
        <div v-if="loading" class="status">Loading your profile...</div>
        <div v-else>
          <form @submit.prevent="saveProfile" enctype="multipart/form-data">
            <div class="form-grid">
              <div class="form-group">
                <label for="first_name">First Name</label>
                <input id="first_name" type="text" v-model="form.first_name" />
              </div>

              <div class="form-group">
                <label for="last_name">Last Name</label>
                <input id="last_name" type="text" v-model="form.last_name" />
              </div>

              <div class="form-group">
                <label for="email">Email</label>
                <input
                id="email"
                type="email"
                v-model="form.email"
                disabled
                class="bg-gray-100 cursor-not-allowed"
                />
              </div>

              <div class="form-group">
                <label for="phone">Phone</label>
                <input id="phone" type="text" v-model="form.phone" />
              </div>

              <div class="form-group">
                <label for="address">Address</label>
                <input id="address" type="text" v-model="form.address" />
              </div>

              <div class="form-group">
                <label for="postal_code">Postal Code</label>
                <input id="postal_code" type="text" v-model="form.postal_code" />
              </div>

              <div class="form-group">
                <label for="city">City</label>
                <input id="city" type="text" v-model="form.city" />
              </div>

              <div class="form-group">
                <label for="birthdate">Birthdate</label>
                <input id="birthdate" type="date" v-model="form.birthdate" />
              </div>

              <div class="form-group">
                <label for="cv">CV</label>
                <div class="file-container">
                  <span v-if="!form.cv">No CV uploaded yet</span>
                  <div v-else>
                    Current CV
                    <ul class="document-list">
                      <li v-if="form.cv && !tempCv">
                        <a :href="form.cv" target="_blank" :title="originalCvName">
                          {{ truncateFilename(originalCvName) }}
                        </a>
                        <button type="button" class="remove-btn" @click="removeCv">X</button>
                      </li>
                      <li v-else-if="tempCv">
                        <a :href="form.cv" target="_blank" :title="originalCvName">
                          {{ truncateFilename(originalCvName) }}
                        </a>
                        <button type="button" class="remove-btn" @click="removeCv">X</button>
                      </li>
                      <li v-else>No CV uploaded yet</li>
                    </ul>
                  </div>
                </div>
                <input
                type="file"
                id="cv"
                ref="cv_input"
                @change="onFileChange('cv', $event)"
                accept=".pdf,.docx, doc, image/*"
                />
              </div>

              <div class="form-group">
                <label for="additional_documents">Additional Documents</label>
                <!-- Container for the list with overflow handling -->
                <div class="file-container">
                  <span v-if="form.additional_documents.length === 0">No document uploaded yet</span>
                  <div v-else>
                    Current Documents
                    <ul class="document-list">
                      <li v-for="doc in form.additional_documents" :key="doc.id">
                        <a :href="doc.file" target="_blank" :title="doc.fileName">{{
                          truncateFilename(doc.fileName)
                        }}</a>
                        <button type="button" class="remove-btn" @click="removeDocument(doc.id)">
                          X
                        </button>
                      </li>
                    </ul>
                  </div>
                </div>
                <!-- Input for new files -->
                <input
                type="file"
                id="additional_documents"
                ref="additional_documents_input"
                @change="onFileChange('additional_documents', $event)"
                multiple
                accept=".pdf,.docx, doc, image/*"
                />
              </div>

              <div class="form-group full-width">
                <label>Profile Picture</label>
                <div class="profile-picture-wrapper">
                  <img
                  :src="preview"
                  @error="onImageError"
                  alt="Profil Picture Loading..."
                  class="profile-picture"
                  />
                </div>
                <input
                type="file"
                id="profile_picture"
                ref="profil_picture_input"
                @change="onFileChange('profile_picture', $event)"
                accept="image/*"
                />
              </div>
            </div>
            <div class="actions">
              <button type="submit" :disabled="saving">
                <span v-if="saving">Saving...</span>
                <span v-else>Save Changes</span>
              </button>
            </div>
            <transition name="fade">
              <div v-if="successMsg || errorMsg">
                <p v-if="successMsg" class="success-msg">{{ successMsg }}</p>
                <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>
              </div>
            </transition>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from "@/services/api"
import authService from "@/services/authService"
import ContentHeader from "@/components/ContentHeader.vue"
import PremiumToggle from "@/components/PremiumToggle.vue"

const ALLOWED_FILE_TYPES = [".pdf", ".docx", ".png", ".jpg", ".jpeg"]

export default {
  name: "JobseekerDetailsView",
  components: {
    ContentHeader,
    PremiumToggle
  },
  data() {
    return {
      form: {
        id: "",
        first_name: "",
        last_name: "",
        email: "",
        phone: "",
        address: "",
        postal_code: "",
        city: "",
        birthdate: "",
        profile_picture: "",
        cv: "",
        additional_documents: []
      },
      tempCv: null,
      tempAdditionalDocuments: [],
      documentsToRemove: [],
      originalCvName: "",
      preview: null,
      loading: true,
      saving: false,
      successMsg: "",
      errorMsg: "",
      cvToRemove: false,
      defaultPlaceholder: "http://localhost:8000/media/profile_pictures/place_holder.png"
    }
  },
  async mounted() {
    try {
      const res = await api.get("/user-profile/")
      this.form = { ...res.data }
      this.preview = this.form.profile_picture
      // CV
      if (this.form.cv) {
        this.originalCvName = this.form.cv.split("/").pop()
      }
      // Additional Documents
      if (Array.isArray(this.form.additional_documents)) {
        this.form.additional_documents = this.form.additional_documents.map((doc) => {
          return {
            ...doc,
            fileName: doc.file.split("/").pop() // Add the file name for each document
          }
        })
      } else {
        // If it's not an array, initialise to an empty array
        this.form.additional_documents = []
      }
    } catch (e) {
      console.error("Cannot load profile:", e)
      this.errorMsg = "Failed to load profile."
    } finally {
      this.loading = false
    }
  },
  methods: {
    truncateFilename(filename = "", maxLength = 15) {
      if (filename.length <= maxLength) return filename
      const start = filename.substring(0, 7)
      const end = filename.substring(filename.length - 6, filename.length)
      return `${start}.....${end}`
    },
    removeDocument(docId) {
      // Add the ID to the list of documents to be removed
      if (!this.documentsToRemove.includes(docId)) {
        this.documentsToRemove.push(docId)
      }
      // Update the displayed documents list
      this.form.additional_documents = this.form.additional_documents.filter(
      (doc) => doc.id !== docId
      )
      this.$refs.additional_documents_input.value = null // Reset the file input
    },
    removeCv() {
      // Reset CV data
      this.form.cv = ""
      this.tempCv = null
      this.originalCvName = ""
      this.cvToRemove = true
      this.$refs.cv_input.value = null // Reset the file input
    },

    validateFile(file) {
      const fileSizeValid = file.size <= 5 * 1024 * 1024 // 5 MB
      const fileTypeValid = ALLOWED_FILE_TYPES.some((ext) => file.name.toLowerCase().endsWith(ext))
      return { fileSizeValid, fileTypeValid }
    },
    onFileChange(field, e) {
      const files = Array.from(e.target.files)
      if (!files.length) return
      files.forEach((file) => {
        const { fileSizeValid, fileTypeValid } = this.validateFile(file)
        if (!fileSizeValid) {
          this.errorMsg = `${file.name} is too large. Max size is 5MB.`
          return
        }
        if (!fileTypeValid) {
          this.errorMsg = `${file.name} is not a valid file type. Allowed types: ${ALLOWED_FILE_TYPES.join(", ")}`
          return
        }
        if (field === "cv") {
          this.tempCv = file // Single file for CV
          this.originalCvName = file.name
          this.form.cv = URL.createObjectURL(file)
        } else if (field === "additional_documents") {
          // Immediately add selected files to the display list
          const newDoc = {
            id: Date.now(), // Temp ID, replaced by the real ID after saving
            file: URL.createObjectURL(file), // For immediate preview
            fileName: file.name,
            isNew: true // Marker to indicate that it has not yet been uploaded
          }
          this.form.additional_documents.push(newDoc)
          this.tempAdditionalDocuments.push(file)
        } else if (field === "profile_picture") {
          this.form.profile_picture = file
          this.preview = URL.createObjectURL(file)
        }
      })
    },
    onImageError(event) {
      event.target.src = this.defaultPlaceholder
    },
    async saveProfile() {
  this.saving = true
  this.successMsg = ""
  this.errorMsg = ""

  // Validation des champs requis
  const requiredFields = ["first_name", "last_name"]
  for (const field of requiredFields) {
    if (!this.form[field] || !this.form[field].toString().trim()) {
      this.errorMsg = `${field.replace("_", " ").charAt(0).toUpperCase() + field.replace("_", " ").slice(1)} is required.`
      this.saving = false
      return
    }
  }
  
  // Validation du format de date
  const birthdateRegex = /^\d{4}-\d{2}-\d{2}$/
  if (!birthdateRegex.test(this.form.birthdate)) {
    this.errorMsg = "Birthdate must be in format YYYY-MM-DD."
    this.saving = false
    return
  }
  
  try {
    const fd = new FormData()
    
    // CORRECTION: Champs à exclure du FormData (même logique que pour l'employeur)
    const fieldsToExclude = ["id", "profile_picture", "cv", "additional_documents", "premium_since", "is_premium"]
    
    // Ajouter tous les champs de texte SAUF ceux exclus
    for (const key in this.form) {
      if (!fieldsToExclude.includes(key)) {
        fd.append(key, this.form[key])
      }
    }
    
    // Ajouter le CV s'il y en a un nouveau
    if (this.tempCv) {
      fd.append("cv", this.tempCv)
    }
    
    // Ajouter les documents additionnels
    if (this.tempAdditionalDocuments.length > 0) {
      this.tempAdditionalDocuments.forEach((file) => {
        fd.append("additional_documents", file)
      })
    }
    
    // Nettoyer tempAdditionalDocuments après traitement
    this.tempAdditionalDocuments = []
    
    // Ajouter les documents à supprimer
    if (this.documentsToRemove.length > 0) {
      this.documentsToRemove.forEach((docId) => {
        fd.append("documents_to_remove", docId)
      })
    }
    
    // Gestion de la suppression de CV
    if (this.cvToRemove) {
      fd.append("cv_to_remove", true)
    }
    
    // Ajouter la photo de profil
    if (this.form.profile_picture instanceof File) {
      fd.append("profile_picture", this.form.profile_picture)
    }
    
    // Envoyer la requête
    const response = await api.patch(`/jobseekers/${this.form.id}/`, fd, {
      headers: { "Content-Type": "multipart/form-data" }
    })
    
    // Mettre à jour le CV en cas de succès
    if (response.data.cv) {
      this.form.cv = response.data.cv
      this.originalCvName = this.tempCv ? this.tempCv.name : this.originalCvName
      this.tempCv = null
    }
    
    // Mettre à jour les documents additionnels s'ils ont été modifiés
    if (response.data.additional_documents) {
      this.form.additional_documents = response.data.additional_documents.map((doc) => {
        return {
          ...doc,
          fileName: doc.file.split("/").pop()
        }
      })
      this.tempAdditionalDocuments = []
    }
    
    // Mettre à jour la photo de profil si elle a été modifiée
    if (response.data.profile_picture) {
      this.form.profile_picture = response.data.profile_picture
      this.preview = response.data.profile_picture
    }
    
    // Réinitialiser la liste des documents à supprimer
    this.documentsToRemove = []
    
    // Mettre à jour le formulaire avec les nouvelles données
    await authService.getUser()

    this.successMsg = "Profile updated successfully!"
    setTimeout(() => {
      this.successMsg = ""
    }, 1500)
    
  } catch (e) {
    console.error("Failed to save profile:", e)
    
    // Gestion des erreurs détaillée (même que pour l'employeur)
    if (e.response?.data) {
      if (typeof e.response.data === 'object') {
        const errors = []
        Object.keys(e.response.data).forEach(key => {
          const value = e.response.data[key]
          if (Array.isArray(value)) {
            errors.push(`${key}: ${value.join(', ')}`)
          } else {
            errors.push(`${key}: ${value}`)
          }
        })
        this.errorMsg = errors.join(' | ')
      } else {
        this.errorMsg = e.response.data.toString()
      }
    } else {
      this.errorMsg = "Failed to save changes."
    }
    
    setTimeout(() => {
      this.errorMsg = ""
    }, 5000)
    
  } finally {
    this.$refs.cv_input.value = null
    this.$refs.additional_documents_input.value = null
    this.$refs.profil_picture_input.value = null
    this.saving = false
    this.cvToRemove = false
  }
}
  }
}
</script>

<style scoped>
.premium-section-container {
  max-width: 700px;
  margin: 2rem auto 0 auto;
  padding: 0 2rem;
}
.profil-page {
  padding: 2rem;
  background: #f5f5f5;
  min-height: 100%;
}
.profil-card {
  background: white;
  max-width: 700px;
  margin: 0 auto;
  padding: 2rem;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
}
h2 {
  margin-bottom: 1.5rem;
  font-size: 2rem;
  color: #044cd3;
  text-align: center;
}
.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}
.form-group {
  display: flex;
  flex-direction: column;
}
.full-width {
  grid-column: 1 / -1;
}
label {
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #374151;
}
input[type="text"],
input[type="email"],
input[type="date"],
input[type="file"] {
  padding: 0.5rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  height: 40px;
  box-sizing: border-box;
}
.profile-picture-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin: 2rem 0;
  position: relative;
}
.profile-picture {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  border: 2px solid #044cd3;
  object-fit: cover;
  font-size: 0.9rem;
  color: #666;
}
.actions {
  text-align: right;
  margin-top: 1.5rem;
}
button {
  background-color: #044cd3;
  color: white;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: bold;
  transition: background 0.2s ease;
}
button:hover {
  background-color: #0335a0;
}
button:disabled {
  background: #a6c8d8;
  cursor: not-allowed;
}
.success-msg {
  margin-top: 1rem;
  color: #2ecc71;
  text-align: center;
  font-weight: 600;
}
.error-msg {
  margin-top: 1rem;
  color: #e74c3c;
  text-align: center;
  font-weight: 600;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
@media (max-width: 768px) {
  .profile-page {
    padding: 1rem;
  }

  .profil-card {
    padding: 1.5rem;
    width: 95%;
    margin: 0 auto;
    border-radius: 8px;
    max-height: 85vh;
    overflow-y: auto;
  }

  .form-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  input[type="text"],
  input[type="email"],
  input[type="date"],
  input[type="file"] {
    width: 100%;
    font-size: 16px; /* Prevents iOS zoom on focus */
  }

  .profile-picture-wrapper {
    margin: 1.5rem 0;
  }

  .actions {
    display: flex;
    justify-content: center;
    margin-top: 1.5rem;
  }

  button {
    width: 100%;
    padding: 0.75rem 1rem;
    font-size: 1rem;
  }

  h2 {
    font-size: 1.5rem;
  }

  label {
    font-size: 0.9rem;
  }
}
.file-container {
  overflow-y: auto;
  padding: 5px;
  border: 1px solid #ccc;
  border-radius: 8px;
  background-color: #fafafa;
  box-sizing: border-box;
}

.document-list {
  list-style-type: none;
  padding: 0;
  margin: 0;
}

.document-list li {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 5px 0;
}

.document-list li a {
  color: #044cd3;
  text-decoration: none;
  flex-grow: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.document-list li a:hover {
  text-decoration: underline;
}
.remove-btn {
  background-color: #e74c3c;
  color: #fff;
  border: none;
  padding: 2px 6px;
  font-size: 12px;
  cursor: pointer;
  margin-left: 10px;
  border-radius: 4px;
}
.remove-btn:hover {
  background-color: #c0392b;
}
</style>
