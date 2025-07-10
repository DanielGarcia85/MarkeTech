import { createRouter, createWebHashHistory } from "vue-router"
import HomeView from "@/views/HomeView.vue"
import EmployerDisplayJobPostsView from "@/views/employer/EmployerDisplayJobPostsView.vue"
import EmployerCreateJobPostView from "@/views/employer/EmployerCreateJobPostView.vue"
import SignupView from "@/views/SignupView.vue"
import LoginView from "@/views/LoginView.vue"
import JobseekerDetailsView from "@/views/jobseeker/JobseekerDetailsView.vue"
import EmployerDetailsView from "@/views/employer/EmployerDetailsView.vue"
import AppointmentView from "@/views/AppointmentView.vue"
import EmployerBookAppointmentView from "@/views/employer/EmployerBookAppointmentView.vue"
import MessagesView from "../views/MessagesView.vue"
import SystemReviewsView from "../views/SystemReviewsView.vue"

const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView
  },
  {
    path: "/messages",
    name: "messages",
    component: MessagesView
  },
  {
    path: "/login",
    name: "login",
    component: LoginView
  },
  {
    path: "/system-reviews",
    name: "systemReviews",
    component: SystemReviewsView
  },
  {
    path: "/signup",
    name: "signup",
    component: SignupView
  },
  {
    path: "/jobseeker/details",
    name: "jobseekerDetails",
    component: JobseekerDetailsView
  },
  {
    path: "/jobseeker/applications",
    name: "jobseekerApplications",
    component: () => import("@/views/jobseeker/JobSeekerApplicationsView.vue"),
    meta: { requiresAuth: true, role: "jobseeker" }
  },
  {
    path: "/employer/details",
    name: "employerDetails",
    component: EmployerDetailsView
  },
  {
    path: "/employer/jobposts",
    name: "employerDisplayJobPostsView",
    component: EmployerDisplayJobPostsView
  },
  {
    path: "/employer/create-jobpost",
    name: "employerCreateJobPostView",
    component: EmployerCreateJobPostView
  },
  {
    path: "/employer/job/:id/applications",
    name: "JobApplicationsView",
    component: () => import("@/views/employer/JobApplicationsView.vue"),
    meta: { requiresAuth: true, role: "employer" }
  },
  {
    path: "/employer/applications",
    name: "EmployerApplicationsOverview",
    component: () => import("@/views/employer/EmployerApplicationsOverview.vue"),
    meta: { requiresAuth: true, role: "employer" }
  },
  {
    path: "/appointments",
    name: "appointments",
    component: AppointmentView
  },
  {
    path: "/employer/book-appointment",
    name: "employerBookAppointment",
    component: EmployerBookAppointmentView,
    meta: { requiresAuth: true, role: "employer" }
  }
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

export default router
