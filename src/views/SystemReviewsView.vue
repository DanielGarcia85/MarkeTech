<template>
  <div class="system-reviews-view">
    <ContentHeader
    title="Rate our platform"
    description="Help us improve MarkeTech by sharing your feedback on the system !"
    />
    <SystemReviews />
  </div>
</template>

<script>
import SystemReviews from "@/components/SystemReviews.vue"
import ContentHeader from "@/components/ContentHeader.vue"

export default {
  name: "SystemReviewsView",
  components: {
    SystemReviews,
    ContentHeader
  }
}
</script>

<style scoped>
.system-reviews-view {
  min-height: 100vh;
  background-color: #f8f8f8;
  padding-bottom: 50px;
}

.page-header {
  text-align: center;
  padding: 40px 20px;
  background-color: #044cd3;
  color: white;
  margin-bottom: 30px;
}

.page-header h1 {
  font-size: 2.2rem;
  margin-bottom: 10px;
}

.page-header p {
  font-size: 1.1rem;
  max-width: 700px;
  margin: 0 auto;
}
</style>
