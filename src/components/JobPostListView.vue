<template>

  <div class="job-posts-container">

    <div class="tabs-container" v-if="isJobSeeker">
      <div class="tab" :class="{ active: !showOnlyFavorites }" @click="showOnlyFavorites = false">
        <i class="fas fa-briefcase"></i> All Jobs
      </div>
      <div class="tab" :class="{ active: showOnlyFavorites }" @click="showOnlyFavorites = true">
        <i class="fas fa-heart"></i> Favorites
        <span v-if="favoritesCount > 0" class="favorites-count">{{ favoritesCount }}</span>
      </div>
    </div>
  </div>
  <!-- modale pop up box -->
  <div v-if="showFavoriteModal" class="modal-overlay" @click.self="cancelAddFavorite">
    <div class="modal-box">
      <h2>Add a Favorite Search</h2>
      <input v-model="favoriteName" type="text" placeholder="Give it a name" />
      <div class="modal-actions">
        <button @click="cancelAddFavorite">Cancel</button>
        <button @click="confirmAddFavorite">Save</button>
      </div>
    </div>
  </div>


  <div class="job-posts-container">
    <!-- Search filter -->
    <div class="filters">
      <input v-model="filters.title" type="text" placeholder="Filter by title" />
      <input v-model="filters.location" type="text" placeholder="Filter by location" />
      <input v-model.number="filters.minSalary" type="number" placeholder="Min salary" />
      <input v-model="filters.postedAfter" type="date" placeholder="Posted after" />
      <button class="reset-btn" @click="resetFilters">Reset Filters</button>
      <button class="add-fav-btn" @click="addFavorite">Add Favorite</button>
    </div>

    <!-- Favorites -->
    <div class="favorites-wrapper mt-4" v-if="favorites.length">
      <div class="favorites-header flex justify-between items-center mb-3">
        <div class="favs-title">My favourite searches</div>
        <button @click="clearFavorites" class="btn-clear">✖ Clear all</button>
      </div>

      <div class="flex flex-wrap gap-5 mt-3">
        <div v-for="(fav, index) in favorites" :key="index" @click="applyFavorite(fav)" class="favorite-badge"
          :title="'Click to reapply this search'">
          <span class="truncate max-w-[200px]">
            {{
              fav.name ||
              (fav.title || "---") +
              " / " +
              (fav.location || "---") +
              " / Min: " +
              (fav.minSalary || "---")
            }}
          </span>
          <button @click.stop="removeFavorite(index)" class="fav-remove-btn" title="Remove">
            <svg xmlns="http://www.w3.org/2000/svg" class="w-4 h-4" fill="none" viewBox="0 0 24 24"
              stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      </div>
    </div>

    <!-- Loading / Jobs -->
    <div v-if="loading" class="text-center text-gray-500">Loading...</div>
    <div v-else>
      <div v-if="showOnlyFavorites && filteredFavoriteJobs.length === 0" class="empty-state">
        <i class="fas fa-heart-broken empty-icon"></i>
        <h3>No favorite jobs yet</h3>
        <p>
          You haven't added any jobs to your favorites. Mark jobs with the heart icon to save them
          here.
        </p>
      </div>

      <JobPostCard v-for="job in displayedJobs" :key="job.id" :job="job" @apply="handleApply"
        @favorite-changed="handleFavoriteChanged" />
    </div>

    <div v-if="!loading && !showOnlyFavorites && jobs.length === 0" class="text-center text-gray-500 mt-6">
      No job offers match your filters.
    </div>

    <!-- Pagination controls -->
    <div v-if="
      !loading &&
      ((!showOnlyFavorites && totalPages > 1) || (showOnlyFavorites && totalFavoritePages > 1))
    " class="pagination">
      <button :disabled="currentPage === 1" @click="changePage(currentPage - 1)">Previous</button>
      <span>
        Page {{ currentPage }} of {{ showOnlyFavorites ? totalFavoritePages : totalPages }}
      </span>
      <button :disabled="currentPage === (showOnlyFavorites ? totalFavoritePages : totalPages)"
        @click="changePage(currentPage + 1)">
        Next
      </button>
    </div>
  </div>
</template>

<script>
import api from "@/services/api"
import JobPostCard from "@/components/JobPostCard.vue"
import authService from "@/services/authService"
import favoriteService from "@/services/favoriteService"
import { createToast } from "mosha-vue-toastify"

export default {
  name: "JobPostListView",
  components: { JobPostCard },
  data() {
    return {
      jobs: [],
      favoriteJobs: [],
      loading: true,
      filters: {
        title: "",
        location: "",
        minSalary: null,
        postedAfter: ""
      },
      favorites: [],
      favoriteName: "",
      showFavoriteModal: false,
      currentPage: 1,
      itemsPerPage: 5,
      totalPages: 1,
      showOnlyFavorites: false
    }
  },
  computed: {
    isJobSeeker() {
      return (
        authService.user.value &&
        authService.user.value.user &&
        authService.user.value.user.groups &&
        authService.user.value.user.groups.includes("jobseeker")
      )
    },
    favoritesCount() {
      return this.favoriteJobs.length
    },
    filteredFavoriteJobs() {
      if (!this.favoriteJobs.length) return []

      const filtered = this.favoriteJobs.filter((job) => {
        const titleMatch =
          !this.filters.title || job.title.toLowerCase().includes(this.filters.title.toLowerCase())
        const locationMatch =
          !this.filters.location ||
          job.location.toLowerCase().includes(this.filters.location.toLowerCase())
        const salaryMatch =
          !this.filters.minSalary || (job.salary_min && job.salary_min >= this.filters.minSalary)
        const dateMatch =
          !this.filters.postedAfter ||
          (job.created_at && new Date(job.created_at) >= new Date(this.filters.postedAfter))

        return titleMatch && locationMatch && salaryMatch && dateMatch
      })

      return filtered.sort((a, b) => {
        if (a.is_employer_premium && !b.is_employer_premium) return -1
        if (!a.is_employer_premium && b.is_employer_premium) return 1
        return new Date(b.created_at) - new Date(a.created_at)
      })
    },
    paginatedFavoriteJobs() {
      const startIndex = (this.currentPage - 1) * this.itemsPerPage
      const endIndex = startIndex + this.itemsPerPage
      return this.filteredFavoriteJobs.slice(startIndex, endIndex)
    },
    totalFavoritePages() {
      return Math.ceil(this.filteredFavoriteJobs.length / this.itemsPerPage)
    },
    displayedJobs() {
      return this.showOnlyFavorites ? this.paginatedFavoriteJobs : this.jobs
    }
  },
  methods: {
    async applyFilters() {
      this.currentPage = 1

      if (this.showOnlyFavorites) {
        this.loading = false
        return
      }

      this.loading = true
      try {
        const params = {
          title: this.filters.title,
          location: this.filters.location,
          salary_min: this.filters.minSalary,
          created_after: this.filters.postedAfter,
          page: this.currentPage
        }
        Object.keys(params).forEach((key) => {
          if (!params[key]) delete params[key]
        })
        const response = await api.get("/jobposts/", { params })
        this.jobs = response.data.results
        this.totalPages = Math.ceil(response.data.count / this.itemsPerPage)

        if (this.isJobSeeker) {
          this.updateFavoriteStatus()
        }
      } catch (error) {
        console.error("Failed to load jobs:", error)
      } finally {
        this.loading = false
      }
    },
    resetFilters() {
      this.filters = {
        title: "",
        location: "",
        minSalary: null,
        postedAfter: ""
      }
      this.currentPage = 1

    },
    async changePage(page) {
      this.currentPage = page

      if (!this.showOnlyFavorites) {
        this.loading = true
        try {
          const params = {
            title: this.filters.title,
            location: this.filters.location,
            salary_min: this.filters.minSalary,
            created_after: this.filters.postedAfter,
            page: this.currentPage
          }

          Object.keys(params).forEach((key) => {
            if (!params[key]) delete params[key]
          })

          const response = await api.get("/jobposts/", { params })
          this.jobs = response.data.results
          this.totalPages = Math.ceil(response.data.count / this.itemsPerPage)

          if (this.isJobSeeker) {
            this.updateFavoriteStatus()
          }
        } catch (error) {
          console.error("Failed to load jobs for page", this.currentPage, ":", error)
        } finally {
          this.loading = false
        }
      }
    },
    handleApply(job) {
      this.$emit("apply", job)
    },

    async fetchFavorites() {
      if (!this.isJobSeeker) return

      try {
        const favorites = await favoriteService.getFavorites()

        this.favoriteJobs = favorites.map((fav) => ({
          id: fav.job_post,
          title: fav.job_title,
          company_name: fav.company_name,
          location: fav.location,
          salary_min: fav.salary_min,
          salary_max: fav.salary_max,
          years_experience: fav.years_experience,
          description: fav.description,
          company_logo: fav.company_logo,
          created_at: fav.created_at,
          is_favorite: true,
          is_employer_premium: fav.is_employer_premium || false
        }))

        this.currentPage = 1
      } catch (error) {
        console.error("Failed to fetch favorites:", error)
      }
    },
    async updateFavoriteStatus() {
      if (!this.isJobSeeker || !this.jobs.length) return

      const jobIds = this.jobs.map((job) => job.id)
      try {
        const favoriteStatuses = await favoriteService.bulkCheckFavorites(jobIds)

        this.jobs.forEach((job) => {
          job.is_favorite = favoriteStatuses[job.id] || false
        })
      } catch (error) {
        console.error("Failed to update favorite statuses:", error)
      }
    },
    handleFavoriteChanged({ jobId, isFavorite }) {
      const job = this.jobs.find((j) => j.id === jobId)
      if (job) {
        job.is_favorite = isFavorite
      }

      if (!isFavorite) {
        this.favoriteJobs = this.favoriteJobs.filter((j) => j.id !== jobId)
      } else {
        this.fetchFavorites()
      }
    },
    loadFavorites() {
      const stored = localStorage.getItem("jobFavorites")
      if (stored) {
        try {
          this.favorites = JSON.parse(stored)
        } catch (e) {
          console.error("Erreur parsing favorites localStorage", e)
        }
      }
    },
    addFavorite() {
      this.favoriteName = ""
      this.showFavoriteModal = true
    },
    confirmAddFavorite() {
      const favorite = {
        name: this.favoriteName,
        title: this.filters.title,
        location: this.filters.location,
        minSalary: this.filters.minSalary,
        postedAfter: this.filters.postedAfter
      }
      this.favorites.push(favorite)
      this.saveFavorites()
      this.showFavoriteModal = false
      createToast("Favorite filter successfully created", {
        type: 'success',
        position: 'bottom-center',
        timeout: 3000,
      });
    },
    cancelAddFavorite() {
      this.showFavoriteModal = false
    },
    removeFavorite(index) {
      this.favorites.splice(index, 1)
    },
    clearFavorites() {
      this.favorites = []
    },
    applyFavorite(fav) {
      this.filters.title = fav.title || ""
      this.filters.location = fav.location || ""
      this.filters.minSalary = fav.minSalary || null
      this.filters.postedAfter = fav.postedAfter || ""
    },
    saveFavorites() {
      localStorage.setItem("jobFavorites", JSON.stringify(this.favorites))
    },
  },
  watch: {
    showOnlyFavorites(newValue) {
      this.currentPage = 1

      if (newValue && this.isJobSeeker) {
        this.fetchFavorites()
      } else {
        this.applyFilters()
      }
    },
    favorites: {
      handler: "saveFavorites",
      deep: true
    },
    filters: {
      handler() {
        if (this.currentPage !== 1) {
          this.currentPage = 1
        }
        this.applyFilters()
      },
      deep: true
    }
  },
  mounted() {
    this.loadFavorites()
    this.applyFilters()


    if (this.isJobSeeker) {
      this.fetchFavorites()
    }

    document.addEventListener("keydown", (e) => {
      if (e.key === "Escape" && this.showFavoriteModal) {
        this.cancelAddFavorite()
      }
    })

  }
}
</script>

<style scoped>
.job-posts-container {
  padding-top: 20px;
  min-height: 100%;
  text-align: center;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 10px;
  margin-bottom: 20px;
}

.filters input {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 6px;
  min-width: 180px;
}

.reset-btn,
.add-fav-btn {
  padding: 8px 12px;
  border-radius: 6px;
  font-weight: bold;
  border: none;
  cursor: pointer;
  color: white;
}

.reset-btn {
  background-color: #044cd3;
}

.reset-btn:hover {
  background-color: #0341b9;
}

.add-fav-btn {
  background-color: #f59e0b;
}

.add-fav-btn:hover {
  background-color: #d97706;
}

.favorites-wrapper {
  border: 1px solid #dbeafe;
  background-color: #f9fafb;
  border-radius: 12px;
  padding: 16px;
  box-shadow: 0 2px 6px rgba(0, 0, 0, 0.04);
  max-width: 100%;
  text-align: left;
}

.favorites-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 4px;
  border-bottom: 1px solid #e5e7eb;
}

.favs-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #2c3e50;
}

.btn-clear {
  background-color: #044cd3;
  color: white;
  border: none;
  padding: 6px 12px;
  font-size: 0.9rem;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
}

.btn-clear:hover {
  background-color: #033aad;
}

.favorite-badge {
  display: inline-flex;
  margin-right: 12px;
  align-items: center;
  background-color: #b1d9ee;
  color: #0c4a6e;
  padding: 10px 20px;
  border-radius: 15px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.favorite-badge:hover {
  background-color: #bae6fd;
  transform: scale(1.03);
}

.fav-remove-btn {
  background: none;
  border: none;
  color: #dc2626;
  margin-left: 8px;
  cursor: pointer;
  transition: color 0.2s ease;
}

.fav-remove-btn:hover {
  color: #b91c1c;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-box {
  background: #fff;
  padding: 20px;
  border-radius: 12px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  width: 90%;
  max-width: 400px;
  box-sizing: border-box;
  overflow: hidden;
}

.modal-box h2 {
  font-size: 1.5rem;
  margin-bottom: 16px;
  text-align: center;
  color: #2c3e50;
}

.modal-box input {
  width: 100%;
  padding: 10px;
  font-size: 1rem;
  border: 1px solid #ccc;
  border-radius: 8px;
  margin-bottom: 16px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
}

.modal-actions button {
  padding: 8px 14px;
  font-size: 1rem;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  min-width: 80px;
}

.modal-actions button:first-child {
  background: #e0e0e0;
  color: #333;
}

.modal-actions button:first-child:hover {
  background: #d0d0d0;
}

.modal-actions button:last-child {
  background: #044cd3;
  color: #fff;
}

.modal-actions button:last-child:hover {
  background: #033aad;
}

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  margin-top: 20px;
}

.pagination button {
  background-color: #044cd3;
  color: white;
  border: none;
  padding: 8px 12px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: bold;
}

.pagination button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.pagination span {
  font-size: 1rem;
  font-weight: bold;
}


.tabs-container {
  display: flex;
  border-bottom: 1px solid #e5e7eb;
  margin-bottom: 20px;
  justify-content: center;
  gap: 20px;
}

.tab {
  padding: 12px 30px;
  font-weight: 500;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 8px;
  position: relative;
  text-align: center;
}

.tab.active {
  color: #044cd3;
  border-bottom: 2px solid #044cd3;
}

.tab:hover:not(.active) {
  color: #4b5563;
  background-color: #f9fafb;
}

.favorites-count {
  background-color: #044cd3;
  color: white;
  border-radius: 9999px;
  font-size: 0.75rem;
  padding: 2px 6px;
  min-width: 20px;
  text-align: center;
}

.empty-state {
  text-align: center;
  padding: 4rem 2rem;
  background-color: white;
  border-radius: 1rem;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  margin: 0 auto;
  max-width: 600px;
}

.empty-icon {
  font-size: 3rem;
  color: #d1d5db;
  margin-bottom: 1rem;
}

.empty-state h3 {
  font-size: 1.5rem;
  margin-bottom: 1rem;
  color: #374151;
}

.empty-state p {
  color: #6b7280;
  margin-bottom: 2rem;
}

@media (max-width: 768px) {
  .filters {
    flex-direction: column;
    align-items: stretch;
  }

  .filters input {
    width: 100%;
    min-width: auto;
  }

  .reset-btn {
    margin-top: 10px;
    width: 100%;
  }

  .pagination {
    flex-wrap: wrap;
  }
}
</style>
