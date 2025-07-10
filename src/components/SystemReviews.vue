<template>
  <div class="system-reviews-container">
    <h2 class="system-reviews-title">System Reviews</h2>

    <!-- Stats Section -->
    <div class="stats-section">
      <div class="stat-card">
        <div class="stat-value">
          {{ stats.average_rating ? stats.average_rating.toFixed(1) : "0.0" }}
        </div>
        <div class="stars">
          <span v-for="i in 5" :key="'avg-' + i" class="star">
            <span v-if="i <= Math.round(stats.average_rating || 0)" class="filled-star">★</span>
            <span v-else class="empty-star">☆</span>
          </span>
        </div>
        <div class="stat-label">Overall Rating</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">
          {{ stats.average_ease ? stats.average_ease.toFixed(1) : "0.0" }}
        </div>
        <div class="stars">
          <span v-for="i in 5" :key="'ease-' + i" class="star">
            <span v-if="i <= Math.round(stats.average_ease || 0)" class="filled-star">★</span>
            <span v-else class="empty-star">☆</span>
          </span>
        </div>
        <div class="stat-label">Ease of Navigation</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">
          {{ stats.average_job_search ? stats.average_job_search.toFixed(1) : "0.0" }}
        </div>
        <div class="stars">
          <span v-for="i in 5" :key="'job-search-' + i" class="star">
            <span v-if="i <= Math.round(stats.average_job_search || 0)" class="filled-star">★</span>
            <span v-else class="empty-star">☆</span>
          </span>
        </div>
        <div class="stat-label">Job Search Effectiveness</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">
          {{
            stats.average_application_process ? stats.average_application_process.toFixed(1) : "0.0"
          }}
        </div>
        <div class="stars">
          <span v-for="i in 5" :key="'application-' + i" class="star">
            <span v-if="i <= Math.round(stats.average_application_process || 0)" class="filled-star">★</span>
            <span v-else class="empty-star">☆</span>
          </span>
        </div>
        <div class="stat-label">Application Process Simplicity</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">
          {{ stats.average_message_system ? stats.average_message_system.toFixed(1) : "0.0" }}
        </div>
        <div class="stars">
          <span v-for="i in 5" :key="'message-' + i" class="star">
            <span v-if="i <= Math.round(stats.average_message_system || 0)" class="filled-star">★</span>
            <span v-else class="empty-star">☆</span>
          </span>
        </div>
        <div class="stat-label">Messaging System</div>
      </div>

      <div class="stat-card">
        <div class="stat-value">{{ stats.total_reviews }}</div>
        <div class="stat-label">Total Reviews</div>
      </div>
    </div>

    <!-- User's Review Section -->
    <div v-if="user" class="user-review-section">
      <h3>{{ userReview ? "Your Review" : "Rate Our System" }}</h3>

      <div class="rating-form">
        <div class="rating-group">
          <label>Overall Rating:</label>
          <div class="star-selector">
            <span v-for="i in 5" :key="'rating-' + i" class="star" :class="{ 'filled-star': i <= review.rating }"
              @click="review.rating = i">
              {{ i <= review.rating ? "★" : "☆" }} </span>
          </div>
        </div>

        <div class="rating-group">
          <label>Ease of Navigation:</label>
          <div class="star-selector">
            <span v-for="i in 5" :key="'ease-rating-' + i" class="star"
              :class="{ 'filled-star': i <= review.ease_of_navigation }" @click="review.ease_of_navigation = i">
              {{ i <= review.ease_of_navigation ? "★" : "☆" }} </span>
          </div>
        </div>

        <div class="rating-group">
          <label>Job Search Effectiveness:</label>
          <div class="star-selector">
            <span v-for="i in 5" :key="'job-search-rating-' + i" class="star"
              :class="{ 'filled-star': i <= review.job_search_effectiveness }"
              @click="review.job_search_effectiveness = i">
              {{ i <= review.job_search_effectiveness ? "★" : "☆" }} </span>
          </div>
        </div>

        <div class="rating-group">
          <label>Application Process:</label>
          <div class="star-selector">
            <span v-for="i in 5" :key="'application-rating-' + i" class="star"
              :class="{ 'filled-star': i <= review.application_process_simplicity }"
              @click="review.application_process_simplicity = i">
              {{ i <= review.application_process_simplicity ? "★" : "☆" }} </span>
          </div>
        </div>

        <div class="rating-group">
          <label>Messaging System:</label>
          <div class="star-selector">
            <span v-for="i in 5" :key="'message-rating-' + i" class="star"
              :class="{ 'filled-star': i <= review.message_system_effectiveness }"
              @click="review.message_system_effectiveness = i">
              {{ i <= review.message_system_effectiveness ? "★" : "☆" }} </span>
          </div>
        </div>

        <div class="comment-input">
          <label for="system-review-comment">Your Feedback:</label>
          <textarea id="system-review-comment" v-model="review.comment" rows="4"
            placeholder="Share your experience with our platform..."></textarea>
        </div>

        <div class="review-actions">
          <button class="submit-review" @click="submitReview" :disabled="!isFormValid">
            {{ userReview ? "Update Review" : "Submit Review" }}
          </button>
        </div>
      </div>
    </div>

    <!-- Login Prompt -->
    <div v-else class="login-prompt">
      <p>Please <router-link to="/login">login</router-link> to leave a review.</p>
    </div>

    <!-- Reviews List -->
    <div class="reviews-list-section">
      <h3>What Others Are Saying</h3>

      <div v-if="loading" class="loading-text">Loading reviews...</div>

      <div v-else-if="reviews.length === 0" class="no-reviews">
        No reviews available yet. Be the first to share your feedback!
      </div>

      <div v-else class="reviews-list">
        <div v-for="review in reviews" :key="review.id" class="review-card">
          <div class="review-header">
            <div class="reviewer-info">
              <strong>{{ review.username }}</strong>
              <span class="review-date">{{ formatDate(review.created_at) }}</span>
            </div>
            <div class="review-ratings">
              <div class="mini-rating">
                <span>Rating:</span>
                <span v-for="i in 5" :key="'list-rating-' + i + review.id" class="mini-star">
                  <span v-if="i <= review.rating" class="filled-star">★</span>
                  <span v-else class="empty-star">☆</span>
                </span>
              </div>
              <div class="mini-rating">
                <span>Ease:</span>
                <span v-for="i in 5" :key="'list-ease-' + i + review.id" class="mini-star">
                  <span v-if="i <= review.ease_of_navigation" class="filled-star">★</span>
                  <span v-else class="empty-star">☆</span>
                </span>
              </div>
              <div class="mini-rating">
                <span>Job Search:</span>
                <span v-for="i in 5" :key="'list-job-' + i + review.id" class="mini-star">
                  <span v-if="i <= review.job_search_effectiveness" class="filled-star">★</span>
                  <span v-else class="empty-star">☆</span>
                </span>
              </div>
              <div class="mini-rating">
                <span>Application:</span>
                <span v-for="i in 5" :key="'list-app-' + i + review.id" class="mini-star">
                  <span v-if="i <= review.application_process_simplicity" class="filled-star">★</span>
                  <span v-else class="empty-star">☆</span>
                </span>
              </div>
              <div class="mini-rating">
                <span>Messaging:</span>
                <span v-for="i in 5" :key="'list-msg-' + i + review.id" class="mini-star">
                  <span v-if="i <= review.message_system_effectiveness" class="filled-star">★</span>
                  <span v-else class="empty-star">☆</span>
                </span>
              </div>
            </div>
          </div>
          <p class="review-comment">{{ review.comment }}</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import systemReviewService from "@/services/systemReviewService"
import authService from "@/services/authService"

export default {
  name: "SystemReviews",
  components: {
  },
  data() {
    return {
      reviews: [],
      stats: {
        average_rating: 0,
        average_ease: 0,
        average_job_search: 0,
        average_application_process: 0,
        average_message_system: 0,
        total_reviews: 0
      },
      userReview: null,
      review: {
        rating: 0,
        ease_of_navigation: 0,
        job_search_effectiveness: 0,
        application_process_simplicity: 0,
        message_system_effectiveness: 0,
        comment: ""
      },
      loading: true,
      submitting: false,
      errorMessage: "",
      showSuccessMessage: "",
    }
  },
  computed: {
    user() {
      return authService.user.value
    },
    isFormValid() {
      return (
        this.review.rating > 0 &&
        this.review.ease_of_navigation > 0 &&
        this.review.job_search_effectiveness > 0 &&
        this.review.application_process_simplicity > 0 &&
        this.review.message_system_effectiveness > 0 &&
        this.review.comment.trim().length > 0
      )
    }
  },
  async created() {
    try {
      this.loadData()
    } catch (error) {
      console.error("Failed to load system reviews:", error)
    }
  },

  watch: {
    // Monitor user changes (login/logout)
    user: {
      immediate: true,
      handler(newUser) {
        if (newUser) {
          this.checkUserReview()
        } else {
          // Reset user notification when logged out
          this.userReview = null
          this.review = {
            rating: 0,
            ease_of_navigation: 0,
            job_search_effectiveness: 0,
            application_process_simplicity: 0,
            message_system_effectiveness: 0,
            comment: ""
          }
        }
      }
    }
  },
  methods: {
    async loadData() {
      try {
        // Load statistics
        this.stats = await systemReviewService.fetchSystemStats()

        // Upload notices
        const response = await systemReviewService.fetchSystemReviews()
        this.reviews = response

        // Check the user's opinion if they are logged in
        if (this.user) {
          await this.checkUserReview()
        }
      } finally {
        this.loading = false
      }
    },

    async checkUserReview() {
      this.userReview = await systemReviewService.getUserReview()
      if (this.userReview) {
        this.review = {
          rating: this.userReview.rating,
          ease_of_navigation: this.userReview.ease_of_navigation,
          job_search_effectiveness: this.userReview.job_search_effectiveness || 0,
          application_process_simplicity: this.userReview.application_process_simplicity || 0,
          message_system_effectiveness: this.userReview.message_system_effectiveness || 0,
          comment: this.userReview.comment
        }
      }
    },

    async submitReview() {
      try {
        this.submitting = true
        this.errorMessage = ""

        if (this.userReview) {
          // Update the existing notice
          const updatedReview = await systemReviewService.updateSystemReview(
            this.userReview.id,
            this.review
          )
          this.userReview = updatedReview

          // Update the notice in the list
          const index = this.reviews.findIndex((r) => r.id === updatedReview.id)
          if (index !== -1) {
            this.reviews.splice(index, 1, updatedReview)
          }

          this.showSuccessMessage = "Your review has been updated!"
        } else {
          // Create a new notice
          const newReview = await systemReviewService.postSystemReview(this.review)
          this.userReview = newReview

          // Add the new notice to the list
          this.reviews.unshift(newReview)

          this.showSuccessMessage = "Thank you for your feedback!"
        }

        // Update statistics
        this.stats = await systemReviewService.fetchSystemStats()

        setTimeout(() => {
          this.showSuccessMessage = ""
        }, 3000)
      } catch (error) {
        this.errorMessage =
          error.message || "There was a problem submitting your review. Please try again."
        setTimeout(() => {
          this.errorMessage = ""
        }, 5000)
      } finally {
        this.submitting = false
      }
    },

    formatDate(datetime) {
      const date = new Date(datetime)
      return date.toLocaleDateString("en-GB", {
        day: "2-digit",
        month: "short",
        year: "numeric"
      })
    }
  }
}
</script>

<style scoped>
.system-reviews-container {
  max-width: 900px;
  margin: 0 auto;
  padding: 30px 20px;
  min-height: 100%;
}

.system-reviews-title {
  font-size: 2rem;
  color: #2c3e50;
  margin-bottom: 30px;
  text-align: center;
}

.stats-section {
  display: flex;
  justify-content: center;
  gap: 20px;
  margin-bottom: 40px;
  flex-wrap: wrap;
}

.stat-card {
  background: white;
  border-radius: 10px;
  padding: 15px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  text-align: center;
  min-width: 140px;
  flex: 1 1 200px;
  max-width: 200px;
  margin-bottom: 15px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #044cd3;
  margin-bottom: 10px;
}

.stars {
  margin-bottom: 10px;
}

.star {
  font-size: 1.5rem;
}

.mini-star {
  font-size: 1rem;
}

.filled-star {
  color: #f8ce0b;
}

.empty-star {
  color: #ddd;
}

.stat-label {
  color: #666;
  font-size: 0.9rem;
  line-height: 1.2;
  height: 2.4em;
  display: flex;
  align-items: center;
  justify-content: center;
}

.user-review-section,
.reviews-list-section {
  background: white;
  border-radius: 10px;
  padding: 25px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.user-review-section h3,
.reviews-list-section h3 {
  margin-bottom: 20px;
  color: #2c3e50;
  font-size: 1.5rem;
}

.rating-form {
  max-width: 600px;
  margin: 0 auto;
}

.rating-group {
  display: flex;
  align-items: center;
  margin-bottom: 15px;
}

.rating-group label {
  width: 180px;
  font-weight: bold;
  color: #333;
}

.star-selector {
  cursor: pointer;
}

.comment-input {
  margin-bottom: 20px;
}

.comment-input label {
  display: block;
  margin-bottom: 8px;
  font-weight: bold;
  color: #333;
}

textarea {
  width: 100%;
  padding: 12px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-family: inherit;
  resize: vertical;
}

.review-actions {
  display: flex;
  justify-content: center;
}

.submit-review {
  background-color: #044cd3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
  font-size: 1rem;
}

.submit-review:disabled {
  background-color: #a5d1d1;
  cursor: not-allowed;
}

.submit-review:hover:not([disabled]) {
  background-color: #0041bb;
}

.error-message {
  background-color: #ffebee;
  color: #e53935;
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-weight: 500;
}

.success-message {
  background-color: #e8f5e9;
  color: #044cd3;
  padding: 10px 15px;
  border-radius: 4px;
  margin-bottom: 15px;
  font-weight: 500;
}

.login-prompt {
  text-align: center;
  padding: 20px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  margin-bottom: 30px;
}

.login-prompt a {
  color: #044cd3;
  font-weight: bold;
  text-decoration: none;
}

.login-prompt a:hover {
  text-decoration: underline;
}

.loading-text,
.no-reviews {
  text-align: center;
  color: #666;
  padding: 15px;
}

.reviews-list {
  display: flex;
  flex-direction: column;
  gap: 15px;
}

.review-card {
  border-bottom: 1px solid #eee;
  padding-bottom: 15px;
}

.review-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  flex-wrap: wrap;
  gap: 10px;
}

.reviewer-info {
  display: flex;
  flex-direction: column;
}

.review-date {
  font-size: 0.8rem;
  color: #888;
}

.review-ratings {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.mini-rating {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.9rem;
}

.review-comment {
  color: #333;
  line-height: 1.5;
}

@media (max-width: 767px) {
  .stat-card {
    min-width: 120px;
    max-width: none;
    flex: 1 1 45%;
  }

  .rating-group {
    flex-direction: column;
    align-items: flex-start;
  }

  .rating-group label {
    margin-bottom: 5px;
    width: 100%;
  }

  .review-header {
    flex-direction: column;
  }

  .review-ratings {
    margin-top: 10px;
  }
}

@media (max-width: 480px) {
  .stat-card {
    min-width: 100%;
    flex: 1 1 100%;
  }
}
</style>
