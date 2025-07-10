<template>
  <div class="job-card" :class="{ 'premium-card': job.is_employer_premium }">
    <div v-if="job.is_employer_premium" class="premium-border"></div>
    <div class="card-header" @click="toggleDetails">
      <div class="job-title-info">
        <div class="title-premium-container">
          <h3>{{ job.title }}</h3>
          <PremiumBadge :isPremium="job.is_employer_premium" variant="small" />
        </div>
        <div class="job-subtitle">
          <span class="company-name">
            {{ job.company_name }}
            <PremiumBadge v-if="job.is_employer_premium" :isPremium="true" variant="small" label="Premium Employer"
              class="company-premium-badge" />
          </span>
          <span class="location"><i class="fas fa-map-marker-alt"></i> {{ job.location }}</span>
        </div>
      </div>

      <div class="toggle-actions">
        <button v-if="isJobSeeker" class="favorite-button" @click.stop="toggleFavorite"
          :class="{ 'is-favorite': isFavorite }" :title="isFavorite ? 'Remove from favorites' : 'Add to favorites'">
          <i :class="isFavorite ? 'fas fa-heart' : 'far fa-heart'"></i>
        </button>
        <div class="toggle-icon" :class="{ rotate: showDetails }">
          <i class="fas fa-chevron-down"></i>
        </div>
      </div>
    </div>

    <transition name="expand" @enter="startTransition" @after-enter="endTransition" @before-leave="startTransition"
      @after-leave="endTransition">
      <div v-if="showDetails" class="job-details-wrapper">
        <div class="description-logo-wrapper">
          <div class="job-description">
            <h4>Description</h4>
            <p>{{ job.description }}</p>
          </div>
          <div class="logo-container">
            <img :src="job.company_logo" :alt="`${job.company_name} logo`" class="company-logo" />
          </div>
        </div>

        <div class="job-info-grid">
          <div class="job-info-item">
            <i class="fas fa-money-bill-wave"></i>
            <div>
              <span class="info-label">Salary</span>
              <span class="info-value">{{ job.salary_min }} – {{ job.salary_max }} CHF</span>
            </div>
          </div>
          <div class="job-info-item">
            <i class="fas fa-user-clock"></i>
            <div>
              <span class="info-label">Experience</span>
              <span class="info-value">{{ job.years_experience }} years</span>
            </div>
          </div>
          <div class="job-info-item">
            <i class="fas fa-building"></i>
            <div>
              <span class="info-label">Company</span>
              <span class="info-value">{{ job.company_name }}</span>
            </div>
          </div>
          <div class="job-info-item">
            <i class="fas fa-calendar-alt"></i>
            <div>
              <span class="info-label">Posted</span>
              <span class="info-value">{{ formatDate(job.created_at) }}</span>
            </div>
          </div>
        </div>

        <div class="job-actions">
          <template v-if="isJobSeeker">
            <button v-if="!hasApplied && !checkingApplication" @click.stop="applyToJob" class="apply-button"
              :class="{ 'premium-apply': job.is_employer_premium }">
              <i class="fas fa-paper-plane"></i> Apply Now
            </button>
            <button v-else-if="hasApplied" class="applied-button" disabled>
              <i class="fas fa-check"></i> Applied
            </button>
            <div v-else class="checking-status">
              <i class="fas fa-spinner fa-spin"></i> Checking status...
            </div>
          </template>

          <slot class="button" name="actions"></slot>
        </div>
      </div>
    </transition>
  </div>
</template>

<script>
import authService from "@/services/authService"
import applicationService from "@/services/applicationService"
import favoriteService from "@/services/favoriteService"
import PremiumBadge from "@/components/PremiumBadge.vue"

export default {
  name: "JobPostCard",
  components: {
    PremiumBadge
  },
  props: {
    job: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      showDetails: false,
      hasApplied: false,
      checkingApplication: true,
      isFavorite: false,
      checkingFavorite: true
    }
  },
  computed: {
    isJobSeeker() {
      return (
        authService.user.value &&
        authService.user.value.user &&
        authService.user.value.user.groups &&
        authService.user.value.user.groups.includes("jobseeker")
      )
    }
  },
  methods: {
    toggleDetails() {
      this.showDetails = !this.showDetails
    },
    formatDate(datetime) {
      const date = new Date(datetime)
      return date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      })
    },
    startTransition(element) {
      element.style.height = "auto"
      const height = getComputedStyle(element).height
      element.style.height = "0"
      element.offsetHeight
      element.style.height = height
    },
    endTransition(element) {
      element.style.height = "auto"
    },
    applyToJob(event) {
      event.stopPropagation()
      this.$emit("apply", this.job)
    },
    async checkApplication() {
      if (this.isJobSeeker && this.job.id) {
        this.checkingApplication = true
        try {
          this.hasApplied = await applicationService.checkIfApplied(this.job.id)
        } catch (error) {
          this.hasApplied = false
        } finally {
          this.checkingApplication = false
        }
      } else {
        this.checkingApplication = false
      }
    },
    async toggleFavorite(event) {
      event.stopPropagation()
      if (!this.isJobSeeker) return

      try {
        const result = await favoriteService.toggleFavorite(this.job.id)
        this.isFavorite = result.status === "added"

        this.$emit("favorite-changed", {
          jobId: this.job.id,
          isFavorite: this.isFavorite
        })
      } catch (error) {
      }
    },

    async checkFavoriteStatus() {
      if (this.isJobSeeker && this.job.id) {
        this.checkingFavorite = true
        try {
          this.isFavorite = await favoriteService.checkFavorite(this.job.id)
        } catch (error) {
          console.error("Failed to check favorite status:", error)
          this.isFavorite = false
        } finally {
          this.checkingFavorite = false
        }
      } else {
        this.checkingFavorite = false
      }
    }
  },
  mounted() {
    this.checkApplication()
    this.checkFavoriteStatus()
  }
}
</script>

<style scoped>
.job-card {
  background: white;
  border: 1px solid #044cd3;
  max-width: 850px;
  margin: 20px auto;
  border-radius: 12px;
  text-align: left;
  overflow: hidden;
  transition:
    transform 0.2s ease,
    box-shadow 0.2s ease;
  position: relative;
}

.job-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
}


.card-header {
  padding: 18px 24px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: white;
  color: #044cd3;
  cursor: pointer;
  transition: background-color 0.3s ease;
}

.card-header:hover {
  background-color: #f0f6ff;
}

.title-premium-container {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.job-title-info h3 {
  margin: 0 0 6px 0;
  font-size: 1.3rem;
  font-weight: 600;
}

.job-subtitle {
  display: flex;
  gap: 15px;
  font-size: 0.95rem;
  opacity: 0.9;
  flex-wrap: wrap;
}

.company-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.company-premium-badge {
  margin-left: 0.25rem;
}

.location {
  display: flex;
  align-items: center;
  gap: 4px;
}

.toggle-icon {
  font-size: 1.1rem;
  transition: transform 0.3s ease;
}

.toggle-icon.rotate i {
  transform: rotate(180deg);
}

.toggle-icon i {
  transition: transform 0.3s ease;
}

.expand-enter-active,
.expand-leave-active {
  transition:
    height 0.3s ease,
    opacity 0.3s ease,
    transform 0.3s ease;
  overflow: hidden;
}

.expand-enter,
.expand-leave-to {
  height: 0;
  opacity: 0;
  transform: translateY(-10px);
}

.job-details-wrapper {
  padding: 0 24px;
  overflow: hidden;
}

.job-details-wrapper>* {
  animation: fade-in 0.4s ease-out forwards;
  animation-delay: 0.1s;
  opacity: 0;
}

@keyframes fade-in {
  from {
    opacity: 0;
    transform: translateY(10px);
  }

  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.description-logo-wrapper {
  display: flex;
  justify-content: space-between;
  gap: 24px;
  margin: 24px 0;
}

.job-description {
  flex: 1;
}

.job-description h4 {
  margin-top: 0;
  margin-bottom: 10px;
  color: #444;
  font-size: 1.1rem;
}

.job-description p {
  margin: 0;
  color: #555;
  line-height: 1.6;
  text-align: justify;
}

.logo-container {
  display: flex;
  align-items: flex-start;
}

.company-logo {
  max-height: 80px;
  max-width: 120px;
  object-fit: contain;
  border-radius: 6px;
  padding: 8px;
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
}

.job-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 25px;
}

.job-info-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.job-info-item i {
  font-size: 1.2rem;
  color: #044cd3;
  width: 24px;
  text-align: center;
}

.info-label {
  display: block;
  font-size: 0.8rem;
  color: #777;
  margin-bottom: 2px;
}

.info-value {
  font-weight: 500;
  color: #333;
}

@media (max-width: 768px) {
  .description-logo-wrapper {
    flex-direction: column;
  }

  .logo-container {
    justify-content: center;
    margin-top: 15px;
  }

  .job-info-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .title-premium-container {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .job-subtitle {
    flex-direction: column;
    gap: 8px;
  }
}

.job-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 20px;
  margin-bottom: 20px;
}

.apply-button,
.applied-button {
  padding: 10px 20px;
  border-radius: 8px;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 8px;
  transition: all 0.2s ease;
  border: none;
  cursor: pointer;
}

.apply-button {
  background-color: #044cd3;
  color: white;
}

.apply-button:hover {
  background-color: #0341b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.apply-button.premium-apply {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #333;
  font-weight: 600;
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.apply-button.premium-apply:hover {
  background: linear-gradient(135deg, #ffed4e, #fff176);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(255, 215, 0, 0.4);
}

.applied-button {
  background-color: #10b981;
  color: white;
  cursor: not-allowed;
}

.checking-status {
  color: #6b7280;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.toggle-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.favorite-button {
  background: none;
  border: none;
  cursor: pointer;
  font-size: 1.2rem;
  color: #999;
  transition:
    transform 0.2s ease,
    color 0.2s ease;
  padding: 5px;
}

.favorite-button:hover {
  transform: scale(1.1);
}

.favorite-button.is-favorite {
  color: #e74c3c;
}
</style>
