import api from "@/services/api"
import router from "@/router"
import { ref } from "vue"

import { createToast } from "mosha-vue-toastify"

let user = ref()

export default {
  user,
  login(payload) {
    if (!payload.username || !payload.password) {
      return Promise.reject("Username and password are required.")
    }

    return api
      .post(`/login/`, payload)
      .then(() => {
        return this.getUser()
      })
      .then(() => {
        createToast("Login successful", {
          type: "success",
          position: "bottom-center",
          timeout: 3000
        })
        return user.value
      })
      .catch((err) => {
        console.error("Login failed:", err)
        return Promise.reject(err)
      })
  },
  logout() {
    return api
      .post("/logout/")
      .then(() => {
        user.value = undefined
        router.push("/")
        createToast("Logout successful", {
          type: "success",
          position: "bottom-center",
          timeout: 3000
        })
      })
      .catch((err) => {
        console.error("Logout failed:", err)
      })
  },
  register(payload) {
    const formData = new FormData()
    for (const key in payload) {
      if (payload[key] !== null && payload[key] !== undefined) {
        formData.append(key, payload[key])
      }
    }

    return api
      .post("/create-profile/", formData)
      .then(() => {
        createToast("Register successful", {
          type: "success",
          position: "bottom-center",
          timeout: 3000
        })
        return this.login({
          username: payload.email,
          password: payload.password
        })
      })
      .catch((err) => {
        console.error("Registration failed:", err)
        return Promise.reject(err)
      })
  },

  getUser() {
    return api
      .get(`/session/`)
      .then((response) => {
        user.value = response.data
      })
      .catch((err) => {
        console.error("Failed to fetch user session:", err)
        user.value = undefined
      })
  }
}
