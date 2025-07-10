<template>
  <div class="premium-toggle-container">
    <div v-if="loading" class="loading">
      <i class="fas fa-spinner fa-spin"></i>
      Loading...
    </div>

    <div v-else class="premium-section">
      <div class="premium-info">
        <div class="premium-icon">
          <i class="fas fa-crown" :class="{ 'active': isPremium }"></i>
        </div>
        <div class="premium-text">
          <h3>Premium Account</h3>
          <p v-if="isPremium" class="premium-active">
            ✨ You are a Premium {{ userType }}! Your {{ userType === 'jobseeker' ? 'applications' : 'job posts' }}
            appear first.
          </p>
          <p v-else class="premium-inactive">
            Upgrade to Premium to boost your visibility and appear at the top of lists!
          </p>
        </div>
      </div>

      <button @click="togglePremium" :disabled="toggling" class="premium-button"
        :class="{ 'premium': isPremium, 'upgrade': !isPremium }" :key="buttonKey">
        <i v-if="toggling" class="fas fa-spinner fa-spin"></i>
        <i v-else-if="isPremium" class="fas fa-star"></i>
        <i v-else class="fas fa-arrow-up"></i>

        <span v-if="toggling">Processing...</span>
        <span v-else-if="isPremium">Premium Active</span>
        <span v-else>Upgrade to Premium</span>
      </button>
    </div>

    <div v-if="message" class="message" :class="messageType">
      {{ message }}
    </div>
  </div>
</template>

<script>
import premiumService from "@/services/premiumService"
import authService from "@/services/authService"

export default {
  name: "PremiumToggle",
  data() {
    return {
      isPremium: false,
      userType: '',
      premiumSince: null,
      loading: true,
      toggling: false,
      message: '',
      messageType: 'success',
      buttonKey: 0
    }
  },

  async mounted() {
    await this.fetchPremiumStatus()
  },

  methods: {
    async fetchPremiumStatus() {
      try {
        this.loading = true
        const data = await premiumService.getPremiumStatus()
        this.isPremium = data.is_premium
        this.userType = data.user_type
        this.premiumSince = data.premium_since

      } catch (error) {
        console.error("Failed to fetch premium status:", error)
        this.showMessage("Failed to load premium status", "error")
      } finally {
        this.loading = false
      }
    },

    async togglePremium() {

      try {
        this.toggling = true
        const data = await premiumService.togglePremium()

        this.isPremium = data.is_premium
        this.userType = data.user_type
        this.buttonKey++

        this.$forceUpdate()

        const statusText = this.isPremium ? "activated" : "deactivated"
        this.showMessage(`Premium status ${statusText} successfully!`, "success")

        this.$emit('premium-changed', {
          isPremium: this.isPremium,
          userType: this.userType
        })

      } catch (error) {
        console.error("Failed to toggle premium:", error)
        this.showMessage("Failed to update premium status", "error")
      } finally {
        this.toggling = false
      }
    },

    showMessage(text, type) {
      this.message = text
      this.messageType = type
      setTimeout(() => {
        this.message = ''
      }, 3000)
    }
  },



}
</script>

<style scoped>
.premium-toggle-container {
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border: 1px solid #dee2e6;
  border-radius: 12px;
  padding: 1.5rem;
  margin: 1rem 0;
}

.loading {
  text-align: center;
  color: #6c757d;
  padding: 1rem;
}

.premium-section {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.premium-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
}

.premium-icon {
  font-size: 2rem;
}

.premium-icon i {
  color: #6c757d;
  transition: all 0.3s ease;
}

.premium-icon i.active {
  color: #ffd700;
  text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
}

.premium-text h3 {
  margin: 0 0 0.5rem 0;
  color: #495057;
  font-size: 1.25rem;
}

.premium-text p {
  margin: 0;
  font-size: 0.9rem;
}

.premium-active {
  color: #28a745;
  font-weight: 500;
}

.premium-inactive {
  color: #6c757d;
}

.premium-button {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border: none;
  border-radius: 8px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
}

.premium-button.upgrade {
  background: linear-gradient(135deg, #007bff, #0056b3);
  color: white;
}

.premium-button.upgrade:hover {
  background: linear-gradient(135deg, #0056b3, #004085);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}

.premium-button.premium {
  background: linear-gradient(135deg, #ffd700, #ffed4e);
  color: #333;
}

.premium-button.premium:hover {
  background: linear-gradient(135deg, #ffed4e, #fff176);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 215, 0, 0.3);
}

.premium-button:disabled {
  opacity: 0.7;
  cursor: not-allowed;
  transform: none;
}

.message {
  margin-top: 1rem;
  padding: 0.75rem;
  border-radius: 6px;
  text-align: center;
  font-weight: 500;
}

.message.success {
  background-color: #d4edda;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.message.error {
  background-color: #f8d7da;
  color: #721c24;
  border: 1px solid #f5c6cb;
}

@media (max-width: 768px) {
  .premium-section {
    flex-direction: column;
    align-items: stretch;
    text-align: center;
  }

  .premium-button {
    justify-content: center;
    width: 100%;
  }
}
</style>
