import api from "@/services/api"

export default {
  fetchSystemReviews() {
    return api
      .get(`system-reviews/`)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error fetching reviews:", error)
        if (error.response) {
          throw new Error(error.response.data.detail || "Failed to load reviews")
        } else if (error.request) {
          throw new Error("Network error - please check your connection")
        } else {
          throw new Error("An unexpected error occurred")
        }
      })
  },

  fetchSystemStats() {
    return api
      .get(`system-reviews/stats/`)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error fetching stats:", error)
        // Return default statistics in the event of an error
        return {
          total_reviews: 0,
          average_rating: 0,
          average_ease: 0,
          average_job_search: 0,
          average_application_process: 0,
          average_message_system: 0
        }
      })
  },

  getUserReview() {
    return api
      .get(`system-reviews/`, { params: { user_id: "me" } })
      .then((response) => {
        if (response.data.length > 0) {
          return response.data[0]
        }
        return null
      })
      .catch((error) => {
        console.error("Error fetching user review:", error)
        return null
      })
  },

  postSystemReview(payload) {
    return api
      .post(`system-reviews/`, payload)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error posting review:", error)
        if (error.response && error.response.data) {
          const errorMessages = []

          // Dealing with Django validation errors
          if (typeof error.response.data === "object") {
            Object.keys(error.response.data).forEach((key) => {
              errorMessages.push(`${key}: ${error.response.data[key]}`)
            })
          } else {
            errorMessages.push(error.response.data)
          }

          throw new Error(errorMessages.join(", "))
        }
        throw new Error("Failed to submit your review")
      })
  },

  updateSystemReview(reviewId, payload) {
    return api
      .put(`system-reviews/${reviewId}/`, payload)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error updating review:", error)
        if (error.response && error.response.data) {
          const errorMessages = []

          if (typeof error.response.data === "object") {
            Object.keys(error.response.data).forEach((key) => {
              errorMessages.push(`${key}: ${error.response.data[key]}`)
            })
          } else {
            errorMessages.push(error.response.data)
          }

          throw new Error(errorMessages.join(", "))
        }
        throw new Error("Failed to update your review")
      })
  }
}
