<template>
  <div>
    <ContentHeader
    title="Make the most of your professional life"
    description="Create an account to access job applications and postings."
    />

    <div class="signup-view">
      <form @submit.prevent="handleSignup">
        <input v-model="email" type="text" placeholder="Email" />
        <input v-model="password" type="password" placeholder="Password" />
        <input v-model="confirmPassword" type="password" placeholder="Confirm Password" />

        <input v-model="first_name" type="text" placeholder="First Name" />
        <input v-model="last_name" type="text" placeholder="Last Name" />
        <input v-model="address" type="text" placeholder="Address" />
        <input v-model="city" type="text" placeholder="City" />
        <input v-model="postal_code" type="text" placeholder="Postal Code" />
        <input v-model="phone" type="text" placeholder="Phone Number" />
        <input v-model="birthdate" type="date" placeholder="Birthdate" />

        <label>Select your role:</label>
        <select v-model="role">
          <option disabled value="">-- Choose a role --</option>
          <option value="jobseeker">Job Seeker</option>
          <option value="employer">Employer</option>
        </select>

        <div v-if="role === 'jobseeker'">
          <label>Profile Picture</label>
          <input type="file" @change="handleFileUpload" />
        </div>

        <div v-if="role === 'employer'">
          <input v-model="company_name" type="text" placeholder="Company Name" />
          <input v-model="company_address" type="text" placeholder="Company Address" />
          <input v-model="company_postal_code" type="text" placeholder="Company Postal Code" />
          <input v-model="company_city" type="text" placeholder="Company City" />
          <input v-model="company_phone" type="text" placeholder="Company Phone" />
          <label>Company Logo</label>
          <input type="file" @change="handleFileUpload" />
        </div>

        <button type="submit" :disabled="isLoading">
          {{ isLoading ? "Creating..." : "Sign Up" }}
        </button>
        <RouterLink to="/login" class="signup-link">
          Already have an account ? <b>Log in</b>
        </RouterLink>

        <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
        <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      </form>
    </div>
  </div>
</template>

<script>
import authService from "@/services/authService"
import api from "@/services/api"
import ContentHeader from "@/components/ContentHeader.vue"

export default {
  name: "SignupView",
  components: {
    ContentHeader
  },
  data() {
    return {
      email: "",
      password: "",
      confirmPassword: "",
      role: "",
      first_name: "",
      last_name: "",
      address: "",
      postal_code: "",
      city: "",
      phone: "",
      birthdate: "",
      profile_picture: null,
      company_name: "",
      company_address: "",
      company_postal_code: "",
      company_city: "",
      company_phone: "",
      company_logo: null,
      isLoading: false,
      errorMessage: "",
      successMessage: ""
    }
  },
  mounted() {
    this.resetForm()
  },
  methods: {
    handleFileUpload(event) {
      if (this.role === "jobseeker") {
        this.profile_picture = event.target.files[0]
      } else if (this.role === "employer") {
        this.company_logo = event.target.files[0]
      }
    },
    handleSignup() {
      this.errorMessage = ""
      this.successMessage = ""
      this.isLoading = true

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

      if (!this.email.trim()) {
        this.errorMessage = "Email is required."
        this.isLoading = false
        return
      }
      if (!emailRegex.test(this.email)) {
        this.errorMessage = "Please enter a valid email address."
        this.isLoading = false
        return
      }
      if (!this.password) {
        this.errorMessage = "Password is required."
        this.isLoading = false
        return
      }
      if (this.password.length < 6) {
        this.errorMessage = "Password must be at least 6 characters."
        this.isLoading = false
        return
      }
      if (!this.confirmPassword) {
        this.errorMessage = "Please confirm your password."
        this.isLoading = false
        return
      }
      if (this.password !== this.confirmPassword) {
        this.errorMessage = "Passwords do not match."
        this.isLoading = false
        return
      }
      if (!this.role) {
        this.errorMessage = "Please select a role."
        this.isLoading = false
        return
      }
      if (!this.first_name.trim()) {
        this.errorMessage = "First name is required."
        this.isLoading = false
        return
      }
      if (!this.last_name.trim()) {
        this.errorMessage = "Last name is required."
        this.isLoading = false
        return
      }
      if (!this.address.trim()) {
        this.errorMessage = "Address is required."
        this.isLoading = false
        return
      }
      if (!this.city.trim()) {
        this.errorMessage = "City is required."
        this.isLoading = false
        return
      }
      if (!this.postal_code.trim()) {
        this.errorMessage = "Postal code is required."
        this.isLoading = false
        return
      }
      if (!this.phone.trim()) {
        this.errorMessage = "Phone number is required."
        this.isLoading = false
        return
      }
      if (!this.birthdate) {
        this.errorMessage = "Birthdate is required."
        this.isLoading = false
        return
      }
      const birthdateRegex = /^\d{4}-\d{2}-\d{2}$/
      if (!birthdateRegex.test(this.birthdate)) {
        this.errorMessage = "Birthdate must be in format YYYY-MM-DD."
        this.isLoading = false
        return
      }
      if (this.role === "employer") {
        if (!this.company_name.trim()) {
          this.errorMessage = "Company name is required."
          this.isLoading = false
          return
        }
        if (!this.company_address.trim()) {
          this.errorMessage = "Company address is required."
          this.isLoading = false
          return
        }
        if (!this.company_postal_code.trim()) {
          this.errorMessage = "Company postal code is required."
          this.isLoading = false
          return
        }
        if (!this.company_city.trim()) {
          this.errorMessage = "Company city is required."
          this.isLoading = false
          return
        }
        if (!this.company_phone.trim()) {
          this.errorMessage = "Company phone is required."
          this.isLoading = false
          return
        }
      }

      // Step 1 : create the profil according to the role
      const profileData = {
        role: this.role,
        first_name: this.first_name,
        last_name: this.last_name,
        address: this.address,
        postal_code: this.postal_code,
        city: this.city,
        phone: this.phone,
        birthdate: this.birthdate,
        email: this.email,
        password: this.password
      }

      if (this.role === "jobseeker") {
        profileData.profile_picture = this.profile_picture
      } else if (this.role === "employer") {
        profileData.company_name = this.company_name
        profileData.company_address = this.company_address
        profileData.company_postal_code = this.company_postal_code
        profileData.company_city = this.company_city
        profileData.company_phone = this.company_phone
        profileData.company_logo = this.company_logo
      }

      authService
      .register(profileData)
      .then(() => {
        this.$router.push("/")
      })
      .catch((err) => {
        this.errorMessage = err.response.data.error
        this.isLoading = false
      })
    },
    resetForm() {
      this.email = ""
      this.password = ""
      this.confirmPassword = ""
      this.role = ""
      this.first_name = ""
      this.last_name = ""
      this.address = ""
      this.postal_code = ""
      this.city = ""
      this.phone = ""
      this.birthdate = ""
      this.profile_picture = null
      this.company_name = ""
      this.company_address = ""
      this.company_postal_code = ""
      this.company_city = ""
      this.company_phone = ""
      this.company_logo = null
      this.errorMessage = ""
      this.successMessage = ""
    }
  }
}
</script>

<style scoped>
.signup-view {
  width: 60%;
  margin: auto;
  margin-top: 50px;
  margin-bottom: 50px;
  padding: 2rem;
  border: 1px solid #ccc;
  border-radius: 10px;
  background: white;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  min-height: 100%;
}

@media (max-width: 768px) {
  .signup-view {
    width: 90%;
    padding: 1.5rem;
    margin-top: 30px;
    margin-bottom: 30px;
  }
}

h2 {
  text-align: center;
  margin-bottom: 1rem;
}

input,
select,
button {
  display: block;
  margin: 5px;
  padding: 10px;
  width: 100%;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

button {
  background-color: #044cd3;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

button:hover {
  background-color: #0041bb;
}

.error-message {
  color: #e74c3c;
  margin-top: 10px;
  font-weight: bold;
  text-align: center;
}

.success-message {
  color: #2ecc71;
  margin-top: 10px;
  font-weight: bold;
  text-align: center;
}
.signup-link {
  display: block;
  text-align: center;
  margin-top: 1rem;
  color: #044cd3;
  text-decoration: none;
}

@media (max-width: 768px) {
  input,
  select,
  button {
    width: 100%;
    box-sizing: border-box;
    margin-left: 0;
    margin-right: 0;
  }
}
</style>
