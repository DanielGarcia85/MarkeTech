import api from "./api"

export default {
  getFavorites() {
    return api
      .get("/job-favorites/")
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error fetching favorites:", error)
        throw error
      })
  },

  toggleFavorite(jobId) {
    return api
      .post(`/jobs/${jobId}/toggle-favorite/`)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error toggling favorite:", error)
        throw error
      })
  },

  checkFavorite(jobId) {
    return api
      .get(`/jobs/${jobId}/check-favorite/`)
      .then((response) => response.data.is_favorite)
      .catch((error) => {
        console.error("Error checking favorite status:", error)
        return false
      })
  },

  bulkCheckFavorites(jobIds) {
    return api
      .post(`/check-favorites/`, { job_ids: jobIds })
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error checking bulk favorite statuses:", error)
        return jobIds.reduce((acc, id) => {
          acc[id] = false
          return acc
        }, {})
      })
  }
}
