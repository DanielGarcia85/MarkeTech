<template>
  <div class="calendar-wrapper">
    <DatePicker v-model="selectedDate" :attributes="calendarAttributes" expanded @dayclick="selectDay"
      :locale="localeSettings" :masks="masks" />

    <div v-if="appointments.length > 0" class="appointments-container">
      <h3>{{ formatDate(selectedDate) }}</h3>

      <div v-if="selectedDayAppointments.length > 0">
        <div v-for="appointment in selectedDayAppointments" :key="appointment.id" class="appointment-item">
          <div class="appointment-header">
            <div class="appointment-time">
              <i class="fas fa-clock"></i>
              {{ formatTime(appointment.appointment_time) }}
            </div>
            <div class="appointment-status" :class="getStatusClass(appointment.status)">
              {{ getStatusLabel(appointment.status) }}
            </div>
          </div>

          <div class="appointment-content">
            <h4 class="job-title">{{ appointment.job_title }}</h4>
            <div class="appointment-details">
              <div class="detail-item">
                <i class="fas fa-building"></i>
                {{ appointment.company_name }}
              </div>
              <div class="detail-item">
                <i class="fas fa-user-tie"></i>
                {{ appointment.employer_name }}
              </div>
              <div class="detail-item">
                <i class="fas fa-user"></i>
                {{ appointment.job_seeker_name }}
              </div>
            </div>
            <div class="appointment-description">
              <h5 class="section-title">Description</h5>
              <div class="description-content">
                <p>{{ appointment.description }}</p>
              </div>
            </div>

            <!-- Response form and details -->
            <div v-if="isJobSeeker && appointment.status === 'pending'" class="response-form">
              <h5 class="section-title">Response</h5>
              <textarea v-model="appointment.responseMessage" placeholder="Write your response here..."
                class="response-textarea"></textarea>
              <div class="response-buttons">
                <button @click="respondToAppointment(appointment.id, 'accepted', appointment.responseMessage)"
                  class="accept-btn">
                  Accept
                </button>
                <button @click="respondToAppointment(appointment.id, 'rejected', appointment.responseMessage)"
                  class="reject-btn">
                  Reject
                </button>
              </div>
            </div>

            <div v-if="['accepted', 'rejected'].includes(appointment.status)" class="response-details">
              <h5 class="section-title">Response from job seeker</h5>
              <div class="response-content">
                <p>{{ appointment.job_seeker_response_message }}</p>
                <div class="response-date">
                  Responded on: {{ formatDateTime(appointment.job_seeker_response_date) }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else class="no-appointments">
        No appointment today
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api';
import authService from '@/services/authService';
import { format, parseISO, isSameDay } from 'date-fns';
import { enUS } from 'date-fns/locale';
import { DatePicker } from 'v-calendar';
import { createToast } from 'mosha-vue-toastify';

export default {
  name: 'AppointmentCalendar',
  components: {
    DatePicker
  },
  data() {
    return {
      appointments: [],
      selectedDate: new Date(),
      isJobSeeker: false,
      localeSettings: {
        id: 'en',
        firstDayOfWeek: 2,
        masks: {
          weekdays: 'WWW',
          title: 'MMMM YYYY',
        }
      },
      masks: {
        weekdays: 'WWW',
        title: 'MMMM YYYY',
        input: 'YYYY-MM-DD'
      }
    };
  },
  async created() {
    const user = authService.user.value;
    this.isJobSeeker = user?.user?.groups?.includes('jobseeker');
  },
  computed: {
    calendarAttributes() {
      const attributes = [
        {
          dates: this.selectedDate,
          highlight: { color: 'blue', fillMode: 'light' }
        }
      ];

      this.appointments.forEach(appointment => {
        let dotColor;
        switch (appointment.status) {
          case 'pending':
            dotColor = 'yellow';
            break;
          case 'accepted':
            dotColor = 'green';
            break;
          case 'rejected':
            dotColor = 'red';
            break;
          default:
            dotColor = 'blue';
        }

        attributes.push({
          dates: parseISO(appointment.appointment_time),
          dot: { color: dotColor }
        });
      });

      return attributes;
    },
    selectedDayAppointments() {
      return this.appointments.filter(appointment =>
        isSameDay(parseISO(appointment.appointment_time), this.selectedDate)
      ).sort((a, b) =>
        new Date(a.appointment_time) - new Date(b.appointment_time)
      );
    }
  },
  mounted() {
    this.loadAppointments();
  },
  methods: {
    async loadAppointments() {
      try {
        const response = await api.get('/user-appointments/');
        this.appointments = response.data;
      } catch (error) {
        console.error('Failed to load appointments:', error);
      }
    },
    selectDay(day) {
      this.selectedDate = day.date;
    },
    formatDate(date) {
      return format(date, 'EEEE d MMMM yyyy', { locale: enUS });
    },
    formatTime(dateString) {
      return format(parseISO(dateString), 'HH:mm');
    },
    getStatusLabel(status) {
      const labels = {
        'pending': 'Pending',
        'accepted': 'Accepted',
        'rejected': 'Rejected'
      };
      return labels[status] || status;
    },

    getStatusClass(status) {
      return `status-${status}`;
    },

    formatDateTime(dateString) {
      if (!dateString) return '';
      return format(parseISO(dateString), 'dd/MM/yyyy HH:mm');
    },
    async respondToAppointment(appointmentId, status, message) {
      if (!message) {
        createToast('Please provide a response message', {
          type: 'warning',
          position: 'bottom-center',
          timeout: 3000,
        });
        return;
      }

      try {
        await api.patch(`/appointments/${appointmentId}/respond/`, {
          status,
          response_message: message
        });

        await this.loadAppointments();
      } catch (error) {
        console.error('Error updating appointment:', error);
      }
    }
  }
};
</script>

<style scoped>
.calendar-wrapper {
  max-width: 700px;
  margin: 0 auto;
}

.appointments-container {
  margin-top: 20px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.appointment-item {
  display: flex;
  flex-direction: column;
  margin-bottom: 16px;
  background: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  overflow: hidden;
}

.appointment-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background-color: #f8fafc;
  border-bottom: 1px solid #e5e7eb;
}

.appointment-time {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
  font-weight: 500;
}

.appointment-time i {
  color: #6b7280;
}

.appointment-content {
  padding: 16px;
}

.job-title {
  margin: 0 0 16px 0;
  font-size: 1.1rem;
  color: #111827;
}

.appointment-details {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 16px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #4b5563;
}

.detail-item i {
  width: 16px;
  color: #6b7280;
}

.appointment-description {
  margin-bottom: 16px;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0 0 8px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.description-content,
.response-content {
  background-color: #f8fafc;
  border-radius: 6px;
  padding: 12px;
}

.description-content p,
.response-content p {
  margin: 0;
  color: #4b5563;
  line-height: 1.5;
}

.response-details {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.response-content .response-date {
  margin-top: 8px;
  font-size: 0.75rem;
  color: #6b7280;
}

.response-form {
  margin-top: 12px;
  border-top: 1px solid #e5e7eb;
  padding-top: 12px;
}

.response-textarea {
  background-color: #f8fafc;
  width: 100%;
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  min-height: 80px;
  margin: 8px 0 12px 0;
  font-size: 0.875rem;
  resize: vertical;
}

.response-buttons {
  display: flex;
  gap: 8px;
}

.accept-btn,
.reject-btn {
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 0.875rem;
  font-weight: 500;
}

.accept-btn {
  background-color: #10b981;
  color: white;
}

.accept-btn:hover {
  background-color: #059669;
}

.reject-btn {
  background-color: #ef4444;
  color: white;
}

.reject-btn:hover {
  background-color: #dc2626;
}

.appointment-status {
  font-size: 0.875rem;
  padding: 4px 12px;
  border-radius: 9999px;
  font-weight: 500;
}

.status-pending {
  background-color: #fef3c7;
  color: #92400e;
  border: 1px solid #f59e0b;
}

.status-accepted {
  background-color: #dcfce7;
  color: #15803d;
  border: 1px solid #22c55e;
}

.status-rejected {
  background-color: #fee2e2;
  color: #b91c1c;
  border: 1px solid #ef4444;
}
</style>
