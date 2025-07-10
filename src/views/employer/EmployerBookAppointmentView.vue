<template>
  <div>
    <ContentHeader title="Book an appointment" description="Schedule an appointment with a candidate." />

    <div class="appointment-container">
      <div class="form-group">
        <label for="jobPost">Select Job Post:</label>
        <select id="jobPost" v-model="selectedJobPost" class="form-control" @change="loadApplications">
          <option value="" disabled>-- Select a job post --</option>
          <option v-for="jobPost in jobPosts" :key="jobPost.id" :value="jobPost.id">
            {{ jobPost.title }}
          </option>
        </select>
      </div>

      <div class="form-group" v-if="selectedJobPost && applications.length > 0">
        <label for="application">Select Candidate:</label>
        <select id="application" v-model="selectedApplication" class="form-control">
          <option value="" disabled>-- Select a candidate --</option>
          <option v-for="application in applications" :key="application.id" :value="application.id">
            {{ application.candidate_name }} ({{ application.candidate_email }})
          </option>
        </select>
      </div>

      <div class="form-group" v-if="selectedApplication">
        <label for="appointmentDate">Select Date and Time:</label>
        <DatePicker expanded mode="dateTime" is24hr v-model="date" :min-date="new Date()" :masks="masks"
          :locale="localeSettings" />
      </div>

      <div class="form-group" v-if="selectedApplication">
        <label for="description">Appointment Description:</label>
        <textarea id="description" v-model="description" class="form-control" rows="4"
          placeholder="Enter details about the appointment..." required></textarea>
      </div>

      <button v-if="selectedApplication" @click="createAppointment" class="btn btn-primary" :disabled="isSubmitting">
        {{ isSubmitting ? 'Scheduling...' : 'Schedule Appointment' }}
      </button>
    </div>
  </div>
</template>

<script>
import ContentHeader from '@/components/ContentHeader.vue'
import { DatePicker } from 'v-calendar';
import api from '@/services/api';
import { createToast } from 'mosha-vue-toastify'

export default {
  name: 'EmployerBookAppointmentView',
  components: {
    ContentHeader,
    DatePicker
  },
  data() {
    return {
      date: new Date(),
      masks: {
        input: 'YYYY-MM-DD HH:mm',
        weekdays: 'WWW',
        title: 'MMMM YYYY'
      },
      localeSettings: {
        id: 'en',
        firstDayOfWeek: 2,
        masks: {
          weekdays: 'WWW',
          title: 'MMMM YYYY'
        }
      },
      jobPosts: [],
      applications: [],
      selectedJobPost: '',
      selectedApplication: '',
      description: '',
      isSubmitting: false,
      error: null
    };
  },
  created() {
    this.fetchJobPosts();
  },
  methods: {
    async fetchJobPosts() {
      try {
        const response = await api.get('/employer-job-posts/');
        this.jobPosts = response.data;
      } catch (error) {
        console.error('Error fetching job posts:', error);
        this.error = 'Failed to load job posts. Please try again later.';
      }
    },
    async loadApplications() {
      if (!this.selectedJobPost) return;

      try {
        const response = await api.get(`/jobposts/${this.selectedJobPost}/applications/`);
        this.applications = response.data;
        this.selectedApplication = '';
      } catch (error) {
        console.error('Error fetching applications:', error);
        this.error = 'Failed to load applications. Please try again later.';
      }
    },
    async createAppointment() {
      if (!this.selectedApplication || !this.date || !this.description.trim()) {
        createToast('Please fill in all required fields', {
          type: 'danger',
          position: 'bottom-center',
          timeout: 3000,
        });
        return;
      }

      this.isSubmitting = true;

      try {
        const appointmentData = {
          job_application: this.selectedApplication,
          appointment_time: this.formatDateTime(this.date),
          description: this.description
        };

        await api.post('/appointments/', appointmentData);

        createToast('Appointment scheduled successfully', {
          type: 'success',
          position: 'bottom-center',
          timeout: 3000,
        });

        this.resetForm();
      } catch (error) {
        console.error('Error creating appointment:', error);
        this.$toast.error('Failed to schedule appointment. Please try again.');
      } finally {
        this.isSubmitting = false;
      }
    },
    formatDateTime(date) {
      return date.toISOString();
    },
    resetForm() {
      this.selectedApplication = '';
      this.date = new Date();
      this.description = '';
    }
  }
}
</script>

<style scoped>
.appointment-container {
  max-width: 600px;
  margin: 0 auto;
  padding: 20px;
  background: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 20px;
}

label {
  display: block;
  margin-bottom: 6px;
  font-weight: 600;
  color: #333;
}

.form-control {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

select.form-control {
  background-position: right 10px center;
  padding-right: 30px;
}

textarea.form-control {
  resize: vertical;
  min-height: 100px;
}

.btn {
  display: inline-block;
  padding: 10px 20px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  text-align: center;
}

.btn-primary {
  background-color: #4e73df;
  color: white;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

@media (max-width: 768px) {
  .appointment-container {
    padding: 15px;
    margin: 0 10px;
  }

  .btn {
    width: 100%;
  }
}
</style>
