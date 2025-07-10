import api from "@/services/api"

export default {
  getApplicationsByJob(jobId) {
    return api
      .get(`jobposts/${jobId}/applications/`)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error fetching applications:", error)
        throw error
      })
  },

  getJobSeekerApplications() {
    return api
      .get(`jobseeker/applications/`)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error fetching jobseeker applications:", error)
        throw error
      })
  },

  async updateApplicationStatus(applicationId, status) {
    try {
      const response = await api.patch(`/applications/${applicationId}/update-status/`, { status })
      return response.data
    } catch (error) {
      console.error("Error updating application status:", error)
      throw error
    }
  },

  submitApplication(jobId, formData) {
    return api
      .post(`jobs/${jobId}/apply/`, formData)
      .then((response) => response.data)
      .catch((error) => {
        console.error("Error submitting application:", error.response?.data || error.message)
        throw error
      })
  },

  checkIfApplied(jobId) {
    return this.getJobSeekerApplications()
      .then((applications) => {
        return applications.some((app) => app.job === jobId)
      })
      .catch((error) => {
        console.error("Error checking application status:", error)
        return false
      })
  },

  async startConversation(applicationId) {
    const response = await api.post("start-conversation/", {
      application_id: applicationId
    })
    return response.data
  }
}
