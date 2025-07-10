<template>
  <div>
    <ContentHeader
    title="Login to marketech"
    description="Access your account to manage job applications and postings."
    />
    <div class="login-view">

      <h2>Welcome back</h2>
      <form @submit.prevent="handleLogin">
        <input type="text" placeholder="Email" v-model="email" />
        <input type="password" placeholder="Password" v-model="password" />
        <button type="submit" class="login-button">Log In</button>
        <router-link to="/signup" class="signup-link">
          Don't have an account ? <b>Sign up</b>
        </router-link>
      </form>

      <p v-if="errorMessage" class="error-message">{{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import authService from "@/services/authService"
import { createToast } from 'mosha-vue-toastify'
import ContentHeader from "@/components/ContentHeader.vue"

export default {
  name: "LoginPage",
  components: {
    ContentHeader
  },
  data() {
    return {
      email: "",
      password: "",
      errorMessage: "",
    }
  },
  methods: {
    handleLogin() {
      this.errorMessage = ""

      // Manual validation
      if (!this.email.trim()) {
        this.errorMessage = "Email is required."
        return
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
      if (!emailRegex.test(this.email)) {
        this.errorMessage = "Please enter a valid email address."
        return
      }

      if (!this.password) {
        this.errorMessage = "Password is required."
        return
      }

      authService
      .login({
        username: this.email,
        password: this.password
      })
      .then((user) => {
        if (user.user.groups.includes("jobseeker")) {
          this.$router.push("/jobseeker/applications")
        } else if (user.user.groups.includes("employer")) {
          this.$router.push("/employer/jobposts")
        } else {
          this.$router.push("/")

        }
      })
      .catch((err) => {
        if (err.response?.data?.errors?.length) {
          this.errorMessage = err.response.data.errors[0].message
        } else {
          createToast("Login failed. Please check your credentials", {
          type: 'danger',
          position: 'bottom-center',
          timeout: 3000,
        });
        }
        console.error(err)
      })
    }
  }
}
</script>

<style scoped>
.login-view {
  background: white;
  padding: 2rem;
  border-radius: 12px;
  width: 60%;
  margin: auto;
  margin-top: 50px;
  margin-bottom: 50px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.2);
  min-height: 100%;
}

@media (max-width: 768px) {
  .login-view {
    width: 90%;
    padding: 1.5rem;
    margin-top: 30px;
    margin-bottom: 30px;
  }
}

h2 {
  margin-bottom: 1rem;
  text-align: center;
}

input,
button {
  display: block;
  margin: 5px;
  padding: 10px;
  width: 100%;
  font-size: 1rem;
  border-radius: 6px;
  border: 1px solid #ccc;
  box-sizing: border-box;
}

button {
  background-color: #044cd3;
  color: white;
  border: none;
  font-weight: bold;
  cursor: pointer;
}

.error-message {
  color: #e74c3c;
  margin-top: 10px;
  font-weight: bold;
  text-align: center;
}

.success-message {
  color: #2ecc71;
  margin-top: 10px;
  font-weight: bold;
  text-align: center;
}
.signup-link {
  display: block;
  text-align: center;
  margin-top: 1rem;
  color: #044cd3;
  text-decoration: none;
}

@media (max-width: 768px) {
  input,
  button {
    width: 100%;
    box-sizing: border-box;
    margin-left: 0;
    margin-right: 0;
  }
}
</style>
