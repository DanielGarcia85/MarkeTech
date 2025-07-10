<template>
  <div>
    <ContentHeader
    title="Change your profile"
    description="Update your employer profile information."
    />
       <div class="premium-section-container">
      <PremiumToggle />
    </div>
    <div class="profile-page">
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
                <label for="company_name">Company Name</label>
                <input id="company_name" type="text" v-model="form.company_name" />
              </div>
              <div class="form-group">
                <label for="company_address">Company Address</label>
                <input id="company_address" type="text" v-model="form.company_address" />
              </div>
              <div class="form-group">
                <label for="company_postal_code">Company Postal Code</label>
                <input id="company_postal_code" type="text" v-model="form.company_postal_code" />
              </div>
              <div class="form-group">
                <label for="company_city">Company City</label>
                <input id="company_city" type="text" v-model="form.company_city" />
              </div>
              <div class="form-group">
                <label for="company_phone">Company Phone</label>
                <input id="company_phone" type="text" v-model="form.company_phone" />
              </div>
              <div class="form-group full-width">
                <label>Company Logo</label>
                <div class="company-logo-wrapper">
                  <img
                  :src="preview"
                  @error="onImageError"
                  alt="Company Logo Loading..."
                  class="company-logo"
                  />
                </div>
                <input type="file" @change="onFileChange" accept="image/*" />
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

export default {
  name: "EmployerDetailsView",
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
        company_name: "",
        company_address: "",
        company_postal_code: "",
        company_city: "",
        company_phone: "",
        company_logo: ""
      },
      file: null,
      preview: null,
      loading: true,
      saving: false,
      successMsg: "",
      errorMsg: "",
      defaultPlaceholder: "/media/company_logos/place_holder.png"
    }
  },
  async mounted() {
    try {
      const res = await api.get("/user-profile/")
      this.form = { ...res.data }
      this.preview = this.form.company_logo
    } catch (e) {
      console.error("Cannot load profile:", e)
      this.errorMsg = "Failed to load profile."
    } finally {
      this.loading = false
    }
  },
  methods: {
    onFileChange(e) {
      const file = e.target.files[0]
      if (!file) return
      this.file = file
      this.preview = URL.createObjectURL(file)
    },
    onImageError(event) {
      event.target.src = this.defaultPlaceholder
    },
    async saveProfile() {
      this.saving = true
      this.successMsg = ""
      this.errorMsg = ""


      const requiredFields = [
        "first_name",
        "last_name", 
        "phone",
        "address",
        "postal_code",
        "city",
        "birthdate",
        "company_name",
        "company_address",
        "company_postal_code", 
        "company_city",
        "company_phone"
      ]
      
      for (const field of requiredFields) {
        if (!this.form[field] || !this.form[field].toString().trim()) {
          this.errorMsg = `${field.replace("_", " ").charAt(0).toUpperCase() + field.replace("_", " ").slice(1)} is required.`
          this.saving = false
          return
        }
      }
      

      const birthdateRegex = /^\d{4}-\d{2}-\d{2}$/
      if (!birthdateRegex.test(this.form.birthdate)) {
        this.errorMsg = "Birthdate must be in format YYYY-MM-DD."
        this.saving = false
        return
      }

      try {
        const fd = new FormData()
        

        const fieldsToExclude = ["id", "company_logo", "premium_since", "is_premium"]
        

        for (const key in this.form) {
          if (!fieldsToExclude.includes(key)) {
            fd.append(key, this.form[key])
          }
        }
        
        if (this.file) {
          fd.append("company_logo", this.file)
        }

      await api.patch(`/employers/${this.form.id}/`, fd, {
  headers: { "Content-Type": "multipart/form-data" }
})
        await authService.getUser()


        this.successMsg = "Profile updated successfully!"
        setTimeout(() => {
          this.successMsg = ""
        }, 1500)
        
      } catch (e) {
        console.error("Failed to save profile:", e)
        
        // Gestion des erreurs détaillée
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
        this.saving = false
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

.profile-page {
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

.company-logo-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  margin: 2rem 0;
  position: relative;
}

.company-logo {
  width: 120px;
  height: 120px;
  border-radius: 0;
  border: 2px solid #044cd3;
  object-fit: contain;
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
  .form-grid {
    grid-template-columns: 1fr;
  }

  .profile-page {
    padding: 1rem;
  }

  .profil-card {
    padding: 1.5rem;
  }
}
</style>