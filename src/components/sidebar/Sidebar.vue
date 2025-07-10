<template>
  <div class="sidebar" :style="{ width: sidebarWidth }">
    <div class="sidebar-content">
      <div v-if="user">
        <h2 :class="{ hidden: collapsed }" style="text-align: center">
          {{ user.profile.first_name }} {{ user.profile.last_name }}
        </h2>

        <!-- Job Seeker -->
        <div v-if="user.user.groups.includes('jobseeker')">
          <img :src="this.user.profile.profile_picture" @error="onImageError" alt="Profile Picture Loading..."
            class="jobseeker-profile-picture" :style="{ width: `calc(${sidebarWidth} * 0.8)`, height: `auto` }" />
        </div>

        <!-- Employer -->
        <div v-if="user.user.groups.includes('employer')">
          <img :src="this.user.profile.company_logo" @error="onImageError" alt="Company Logo Loading..."
            class="employer-profile-picture" :style="{ width: `calc(${sidebarWidth} * 0.8)`, height: `auto` }" />
        </div>
        <!-- Job Seeker Links -->
        <div v-if="user.user.groups.includes('jobseeker')">
          <SidebarLink to="/jobseeker/applications" icon="fas fa-file-alt">My applications</SidebarLink>
        </div>

        <!-- Employer Links -->
        <div v-if="user.user.groups.includes('employer')">
          <SidebarLink to="/employer/jobposts" icon="fa-solid fa-folder-open">My job posts</SidebarLink>
          <SidebarLink to="/employer/applications" icon="fas fa-users">
            Manage applications
          </SidebarLink>
          <SidebarLink to="/employer/book-appointment" icon="fa-solid fa-calendar-plus">Book an appointment
          </SidebarLink>
        </div>

        <!-- Messages Link (visible à tous les connectés) -->
        <SidebarLink to="/messages" icon="fas fa-comments">Messages</SidebarLink>
        <SidebarLink to="/" icon="fa-solid fa-envelope">Job offers</SidebarLink>
        <SidebarLink to="/appointments" icon="fa-solid fa-calendar-days">My appointments</SidebarLink>
        <SidebarLink to="/system-reviews" icon="fas fa-star">System reviews</SidebarLink>

      </div>

      <div v-else>
        <SidebarLink to="/" icon="fas fa-home">Home</SidebarLink>
        <SidebarLink to="/login" icon="fa-solid fa-right-to-bracket">Login</SidebarLink>
        <SidebarLink to="/signup" icon="fa-solid fa-user-plus">Sign up</SidebarLink>
      </div>

      <span class="collapse-icon" :class="{ 'rotate-180': collapsed }" @click="toggleSidebar">
        <i class="fas fa-angle-double-left" />
      </span>
    </div>
  </div>
</template>

<script>
import SidebarLink from "./SidebarLink.vue"
import { collapsed, toggleSidebar, sidebarWidth } from "./state"
import authService from "@/services/authService"

export default {
  data() {
    return {
      defaultProfilPicturePlaceholder: "/media/profile_pictures/place_holder.png",
      defaultCompanyLogoPlaceholder: "/media/company_logos/place_holder.png"
    }
  },
  props: {},
  components: { SidebarLink },
  setup() {
    return { collapsed, toggleSidebar, sidebarWidth }
  },
  computed: {
    user() {
      return authService.user.value
    }
  },
  methods: {
    logout() {
      authService.logout()
    },
    onImageError(event) {
      if (this.user.user.groups.includes("employer")) {
        event.target.src = this.defaultCompanyLogoPlaceholder
      } else if (this.user.user.groups.includes("jobseeker")) {
        event.target.src = this.defaultProfilPicturePlaceholder
      }
    }
  }
}
</script>

<style>
:root {
  --sidebar-bg-color: #044cd3;
  --sidebar-item-hover: #0041bb;
  --sidebar-item-active: #2168ec;
}
</style>

<style scoped>
.sidebar {
  color: white;
  background-color: var(--sidebar-bg-color);
  float: left;
  position: fixed;
  z-index: 1;
  top: 0;
  left: 0;
  bottom: 0;
  padding: 0.5em;
  transition: 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar-content {
  margin-top: 100px;
}


.collapse-icon {
  position: absolute;
  top: 0;
  right: 0;
  padding: 0.75em;
  color: rgba(255, 255, 255, 0.7);
  transition: 0.2s linear;
}

.rotate-180 {
  transform: rotate(180deg);
  transition: 0.2s linear;
}

.jobseeker-profile-picture {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid black;
  object-fit: cover;
  margin: 1rem auto;
  display: block;
  transition: 0.2s linear;
  background-color: rgba(255, 255, 255, 0.7);
}

.employer-profile-picture {
  width: 100%;
  height: auto;
  border-radius: 0;
  border: 2px solid black;
  object-fit: contain;
  margin: 1rem auto;
  display: block;
  transition: 0.2s linear;
  background-color: rgb(255, 255, 255);
}

.hidden {
  visibility: hidden;
}

.sidebar-logo {
  width: 100%;
  margin: 0.5rem auto;
  display: block;
  transition: 0.3s ease;
}
</style>
