import api from "./api"

export default {
  async fetchConversations() {
    const response = await api.get("/conversations/", {
      withCredentials: true
    })
    return response.data
  },

  async fetchMessages(applicationId) {
    const response = await api.get(`/applications/${applicationId}/messages/`)
    return response.data
  },

  async postMessage({ body, subject, application }) {
    const response = await api.post(`/applications/${application}/messages/`, {
      subject,
      body
    })
    return response.data
  }
}
