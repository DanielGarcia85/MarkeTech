<template>
  <div>
    <ContentHeader title="Find your dream job"
      description="Browse through our job listings and apply for your dream job." />

    <!-- Liste des offres -->
    <JobPostListView @apply="showApplicationForm" />

    <!-- Formulaire de candidature -->
    <JobApplicationForm v-if="selectedJob" :show="showApplicationModal" :job="selectedJob" @close="closeApplicationForm"
      @submitted="handleApplicationSubmitted" />
  </div>
</template>

<script>
import JobPostListView from "@/components/JobPostListView.vue"
import JobApplicationForm from "@/views/jobseeker/JobApplicationForm.vue"
import ContentHeader from "@/components/ContentHeader.vue"
import { ref } from "vue"
import { createToast } from "mosha-vue-toastify"

export default {
  name: "HomeView",
  components: {
    JobPostListView,
    JobApplicationForm,
    ContentHeader
  },
  setup() {
    const selectedJob = ref(null)
    const showApplicationModal = ref(false)

    function showApplicationForm(job) {
      selectedJob.value = job
      showApplicationModal.value = true
    }

    function closeApplicationForm() {
      showApplicationModal.value = false
      setTimeout(() => {
        selectedJob.value = null
      }, 300)
    }

    function handleApplicationSubmitted() {
      createToast("Application submitted successfully", {
        type: 'success',
        position: 'bottom-center',
        timeout: 3000,
      });
    }

    return {
      selectedJob,
      showApplicationModal,
      showApplicationForm,
      closeApplicationForm,
      handleApplicationSubmitted
    }
  }
}
</script>
