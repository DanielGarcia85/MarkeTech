<template>
  <footer class="footer">
    <div class="footer-content">
      <div class="footer-section">
        <h3>MarkeTech</h3>
        <p>Your trusted platform for job seekers and employers.</p>
      </div>
      <div class="footer-section">
        <h3>Latest Reviews</h3>
        <div v-if="loading" class="loading">Loading reviews...</div>
        <ul v-else>
          <li v-for="review in latestReviews" :key="review.id" class="review-item">
            <div class="stars">
              <span v-for="n in 5" :key="n" class="star">
                {{ n <= review.rating ? '★' : '☆' }} </span>
            </div>
            <p class="review-comment">{{ truncateText(review.comment) }}</p>
            <span class="review-author">- {{ review.username }}</span>
          </li>
        </ul>
        <router-link to="/system-reviews" class="view-all-btn" @click="scrollToTop">
          View All Reviews <i class="fas fa-arrow-right"></i>
        </router-link>
      </div>
      <div class="footer-section">
        <h3>Follow Us</h3>
        <div class="social-icons">
          <a href="https://www.facebook.com" target="_blank"><i class="fab fa-facebook"></i></a>
          <a href="https://www.x.com" target="_blank"><i class="fab fa-twitter"></i></a>
          <a href="https://www.linkedin.com" target="_blank"><i class="fab fa-linkedin"></i></a>
        </div>
      </div>
    </div>
    <div class="footer-bottom">
      <p>&copy; 2025 MarkeTech. All rights reserved.</p>
    </div>
  </footer>
</template>

<script>
import systemReviewService from "@/services/systemReviewService"

export default {
  name: "Footer",
  data() {
    return {
      latestReviews: [],
      loading: true
    }
  },
  methods: {
    truncateText(text) {
      return text.length > 50 ? text.substring(0, 50) + '...' : text
    },
    async fetchLatestReviews() {
      try {
        const reviews = await systemReviewService.fetchSystemReviews()
        this.latestReviews = reviews.slice(0, 3)
      } catch (error) {
        console.error('Error fetching reviews:', error)
      } finally {
        this.loading = false
      }
    },
    scrollToTop() {
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      })
    }
  },
  mounted() {
    this.fetchLatestReviews()
  }
}
</script>

<style scoped>
.footer {
  background: linear-gradient(to right, rgba(4, 76, 211, 0.05), rgba(4, 76, 211, 0.01));
  color: #5a6a7e;
  padding: 2rem 1.5rem;
  border-radius: 0.75rem;
  margin-top: 2rem;
}

.footer-content {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 2rem;
}

.footer-section {
  flex: 1;
  min-width: 200px;
}

.footer-section h3 {
  color: #2c3e50;
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 1rem;
  position: relative;
  display: inline-block;
}

.footer-section h3::after {
  content: "";
  position: absolute;
  bottom: -0.5rem;
  left: 0;
  width: 100%;
  height: 0.25rem;
  background-color: #044cd3;
  border-radius: 1rem;
}

.footer-section p,
.footer-section ul {
  margin: 0;
  padding: 0;
  list-style: none;
}

.footer-section ul li {
  margin: 0.75rem 0;
}

.footer-section ul li a {
  color: #5a6a7e;
  text-decoration: none;
  transition: color 0.3s ease;
  cursor: pointer;
}

.footer-section ul li a:hover {
  color: #044cd3;
}

.social-icons {
  display: flex;
  gap: 1rem;
}

.social-icons a {
  color: #5a6a7e;
  font-size: 1.5rem;
  transition: color 0.3s ease;
}

.social-icons a:hover {
  color: #044cd3;
}

.footer-bottom {
  margin-top: 2rem;
  padding-top: 1rem;
  border-top: 1px solid rgba(4, 76, 211, 0.1);
  font-size: 0.9rem;
  color: #5a6a7e;
  text-align: center;
}

.review-item {
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.stars {
  color: #f8ce0b;
  margin-bottom: 0.25rem;
}

.review-comment {
  color: #5a6a7e;
  margin: 0.25rem 0;
  font-style: italic;
}

.review-author {
  color: #044cd3;
  font-weight: 500;
  font-size: 0.8rem;
}

.loading {
  color: #5a6a7e;
  font-style: italic;
  font-size: 0.9rem;
}

.view-all-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 1rem;
  padding: 0.5rem 1rem;
  background-color: #044cd3;
  color: white;
  text-decoration: none;
  border-radius: 0.5rem;
  font-size: 0.9rem;
  transition: all 0.3s ease;
}

.view-all-btn:hover {
  background-color: #033aad;
  transform: translateX(5px);
}

@media (max-width: 768px) {
  .footer {
    padding: 1.5rem 1rem;
  }

  .footer-content {
    flex-direction: column;
    gap: 1.5rem;
  }

  .footer-section {
    text-align: center;
  }

  .footer-section h3::after {
    left: 50%;
    transform: translateX(-50%);
  }

  .social-icons {
    justify-content: center;
    margin-top: 0.5rem;
  }
}
</style>
