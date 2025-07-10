<template>
  <div v-if="user">
    <Sidebar />
    <div class="section" :style="{ marginLeft: `calc(${sidebarWidth} + 1em)` }">
      <Navbar />
      <router-view class="content" />
      <Footer />
    </div>
  </div>
  <div v-else>
    <div class="section">
      <Navbar />
      <router-view class="content" />
      <Footer />
    </div>
  </div>

</template>

<script>
import Navbar from "@/components/navbar/NavBar.vue"
import Sidebar from "@/components/sidebar/Sidebar.vue"
import Footer from "@/components/footer/Footer.vue"
import { sidebarWidth } from "@/components/sidebar/state"
import authService from "@/services/authService"

export default {
  components: {
    Sidebar,
    Navbar,
    Footer
  },
  setup() {
    return {
      sidebarWidth
    }
  },
  computed: {
    user() {
      return authService.user.value
    }
  },
  mounted() {
    authService.getUser()
  }
}
</script>

<style>
* {
  margin: 0;
  padding: 0;
}

/* Styles spécifiques pour les formulaires mobiles */
@media (max-width: 768px) {
  .login-view form input,
  .login-view form button,
  .signup-view form input,
  .signup-view form select,
  .signup-view form button,
  .modal-box input,
  .modal-box button,
  .modal-container input,
  .modal-container select,
  .modal-container textarea,
  .modal-container button,
  .create-jobpost-view form input,
  .create-jobpost-view form textarea,
  .create-jobpost-view form button {
    width: 100%;
    box-sizing: border-box;
  }
}

body {
  font-family: "Roboto", "Helvetica Neue", Arial, sans-serif;
  background-color: rgba(0, 0, 0, 0.05);
}

.section {
  transition: margin-left 0.3s ease;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.content {
  flex-grow: 1;
}

/* Styles globaux pour les formulaires */
input, select, textarea, button {
  box-sizing: border-box;
  max-width: 100%;
}

@media (max-width: 768px) {
  form {
    width: 100%;
  }

  input, select, textarea, button {
    width: 100%;
    margin-left: 0;
    margin-right: 0;
  }
}
</style>
