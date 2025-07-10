<template>
  <nav class="navbar">
    <div class="navbar-container">
      <div class="navbar-logo">
        <router-link to="/">
          <img src="@/assets/marketech_logo2_navbar.png" alt="MarkeTech Logo" class="logo-image" />
        </router-link>
      </div>
      <div class="navbar-links">
        <div v-if="user" class="user-menu">
          <div v-if="user.user.groups.includes('jobseeker')">
            <router-link to="/jobseeker/details" class="nav-link profile-btn">
              <i class="fas fa-user"></i>
              <span>My profile</span>
            </router-link>
          </div>
          <div v-if="user.user.groups.includes('employer')">
            <router-link to="/employer/details" class="nav-link profile-btn">
              <i class="fas fa-user"></i>
              <span>My profile</span>
            </router-link>
          </div>
          <a href="#" @click.prevent="logout" class="nav-link logout-btn">
            <i class="fas fa-sign-out-alt"></i>
            <span>Logout</span>
          </a>
        </div>
        <div v-else class="auth-links">
          <router-link to="/login" class="nav-link login-btn">
            <i class="fas fa-sign-in-alt"></i>
            <span>Login</span>
          </router-link>
          <router-link to="/signup" class="nav-link register-btn">
            <i class="fas fa-user-plus"></i>
            <span>Register</span>
          </router-link>
        </div>
      </div>
    </div>
  </nav>
</template>

<script>
import authService from "@/services/authService"
export default {
  name: 'Navbar',
  data() {
    return {
    }
  },  computed: {
    user() {
      return authService.user.value
    }
  },
  methods: {
    logout() {
      authService.logout()
    }
  }
}
</script>

<style scoped>
.navbar {
  position: sticky;
  top: 0;
  width: 100%;
  background-color: #ffffff;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  z-index: 1000;
  padding: 0.5rem 0;
}

.navbar-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 2rem;
  height: 70px;
  max-width: 1200px;
  margin: 0 auto;
}

.navbar-logo {
  display: flex;
  align-items: center;
}

.navbar-logo a {
  display: flex;
  align-items: center;
  text-decoration: none;
  color: #333;
}

.logo-image {
  height: 50px;
  margin-right: 10px;
  transition: transform 0.3s ease;
}

.logo-image:hover {
  transform: scale(1.05);
}

.navbar-links {
  display: flex;
  gap: 20px;
}

.user-menu, .auth-links {
  display: flex;
  gap: 12px;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 6px;
  text-decoration: none;
  font-weight: 500;
  padding: 8px 16px;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.nav-link i {
  font-size: 1rem;
}


.login-btn {
  background-color: #044cd3;
  color: white;
}

.login-btn:hover {
  background-color: #0341b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(4, 76, 211, 0.2);
}

.profile-btn{
  background-color: #044cd3;
  color: white;
}
.profile-btn:hover {
  background-color: #0341b9;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(4, 76, 211, 0.2);
}



.register-btn {
  background-color: #f0f0f0;
  color: #333;
  border: 1px solid #e0e0e0;
}

.register-btn:hover {
  background-color: #e0e0e0;
  transform: translateY(-2px);
}

.logout-btn {
  background-color: #ef4444;
  color: white;
}

.logout-btn:hover {
  background-color: #dc2626;
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(239, 68, 68, 0.2);
}

/* Responsive styles */
@media (max-width: 768px) {
  .navbar-container {
    padding: 0 1rem;
    height: auto;
    flex-direction: column;
    padding: 10px 0;
  }

  .navbar-logo {
    margin-bottom: 10px;
    justify-content: center;
  }

  .navbar-links {
    width: 100%;
    justify-content: center;
  }

  .user-menu, .auth-links {
    width: 100%;
    justify-content: center;
  }
}
</style>
