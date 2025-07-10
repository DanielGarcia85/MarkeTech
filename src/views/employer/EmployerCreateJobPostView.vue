<template>
  <div>
    <ContentHeader title="Create a new job post"
      description="Fill in the details below to create a new job post for your company." />
    <div class="create-jobpost-view">
      <div class="header">
      </div>
      <form @submit.prevent="submitJobPost">
        <div class="form-group">
          <label for="title">Job Title</label>
          <input type="text" id="title" v-model="form.title" required />
        </div>

        <div class="form-group">
          <label for="description">Description</label>
          <textarea style="height: 100px" id="description" v-model="form.description" required></textarea>
        </div>

        <div class="form-group">
          <label for="location">Location</label>
          <input type="text" id="location" v-model="form.location" required />
        </div>

        <div class="form-group">
          <label for="salary_min">Minimum Salary</label>
          <input type="number" id="salary_min" v-model="form.salary_min" required />
        </div>

        <div class="form-group">
          <label for="salary_max">Maximum Salary</label>
          <input type="number" id="salary_max" v-model="form.salary_max" required />
        </div>

        <div class="form-group">
          <label for="years_experience">Years of Experience</label>
          <input type="number" id="years_experience" v-model="form.years_experience" required />
        </div>

        <div class="form-actions">
          <button type="submit" class="btn">Create</button>
          <button type="button" class="btn cancel-btn" @click="cancelJobPost">Cancel</button>
        </div>
      </form>

      <p v-if="successMessage" class="success-message">{{ successMessage }}</p>
      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import api from "@/services/api"
import ContentHeader from "@/components/ContentHeader.vue"
import { createToast } from 'mosha-vue-toastify';

export default {
  name: "EmployerCreateJobPostsView",
  components: {
    ContentHeader
  },
  data() {
    return {
      form: {
        title: "",
        description: "",
        location: "",
        salary_min: "",
        salary_max: "",
        years_experience: ""
      },
      successMessage: "",
      errorMessage: ""
    }
  },
  methods: {
    submitJobPost() {
      api.post("/employer-job-posts/", this.form)
        .then((response) => {
          this.errorMessage = ""
          this.resetForm()
          createToast("Job post created successfully", {
            type: 'success',
            position: 'bottom-center',
            timeout: 3000,
          });
          this.$router.push('/employer/jobposts')
        })
        .catch((error) => {
          if (error.response && error.response.data && error.response.data.error) {
            // Retrieve the specific error message from the backend
            this.errorMessage = error.response.data.error
          } else {
            // Generic error message if no specific message available
            this.errorMessage = "Failed to create job post. Please try again."
          }
          this.successMessage = ""
        })
    },
    resetForm() {
      this.form = {
        title: "",
        description: "",
        location: "",
        salary_min: "",
        salary_max: "",
        years_experience: "",
        company_name: "",
        company_logo: "",
        is_visible: false
      }
    },
    cancelJobPost() {
      this.$router.go(-1)
    }
  }
}
</script>

<style scoped>
.create-jobpost-view {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 60%;
  margin: auto;
  margin-top: 50px;
  margin-bottom: 50px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  min-height: 100%;
}

h1 {
  margin-bottom: 1rem;
  text-align: left;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}

input,
textarea,
button {
  display: block;
  margin: 5px 0;
  padding: 10px;
  width: 100%;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

textarea {
  resize: vertical;
  overflow: auto;
}

button {
  background-color: #044cd3;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
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

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.form-actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
}

.cancel-btn {
  background-color: #ef4444;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
  padding: 10px 20px;
  border-radius: 6px;
}

.cancel-btn:hover {
  background-color: #dc2626;
}

@media (max-width: 768px) {

  input,
  textarea,
  button {
    width: 100%;
    box-sizing: border-box;
  }

  .create-jobpost-view {
    width: 90%;
  }

  .form-actions {
    flex-direction: column;
  }
}
</style>
