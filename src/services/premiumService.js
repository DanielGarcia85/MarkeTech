import api from "./api"

export default {
  /**
   * Basculer le statut premium de l'utilisateur connecté
   */
  async togglePremium() {
    try {
      const response = await api.post("/toggle-premium/")
      return response.data
    } catch (error) {
      console.error("Error toggling premium status:", error)
      throw error
    }
  },

  /**
   * Récupérer le statut premium de l'utilisateur connecté
   */
  async getPremiumStatus() {
    try {
      const response = await api.get("/premium-status/")
      return response.data
    } catch (error) {
      console.error("Error fetching premium status:", error)
      throw error
    }
  }
}