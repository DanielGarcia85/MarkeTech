<template>
  <div class="content-header">
    <div class="content-header-container">
      <h1 class="content-header-title">{{ title }}</h1>
      <div class="content-header-description">
        <p>{{ description }}</p>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ContentHeader',
  props: {
    title: {
      type: String,
      required: true
    },
    description: {
      type: String,
      default: ''
    }
  }
}
</script>

<style scoped>
.content-header {
  padding: 2rem 1.5rem;
  position: relative;
  background: linear-gradient(to right, rgba(4, 76, 211, 0.05), rgba(4, 76, 211, 0.01));
  border-radius: 0.75rem;
  overflow: hidden;
  text-align: center;
}

.content-header-container {
  position: relative;
  z-index: 2;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.content-header-title {
  font-size: 2rem;
  font-weight: 700;
  color: #2c3e50;
  margin-bottom: 0.75rem;
  line-height: 1.2;
  position: relative;
  display: inline-block;
}

.content-header-title::after {
  content: '';
  position: absolute;
  bottom: -0.5rem;
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  height: 0.25rem;
  background-color: #044cd3;
  border-radius: 1rem;
}

.content-header-description {
  width: 100%;
  color: #5a6a7e;
  font-size: 1.1rem;
  line-height: 1.6;
  margin-top: 0.5rem;
}


@media (max-width: 768px) {
  .content-header {
    padding: 1.5rem 1rem;
    margin-bottom: 1.5rem;
  }

  .content-header-title {
    font-size: 1.75rem;
  }

  .content-header-description {
    font-size: 1rem;
  }
}
</style>
