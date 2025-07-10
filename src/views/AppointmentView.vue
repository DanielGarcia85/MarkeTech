<template>
  <div>
    <ContentHeader title="My appointments" description="View your scheduled appointments." />
    <Calendar />
  </div>
</template>

<script>
import ContentHeader from '@/components/ContentHeader.vue'
import Calendar from '@/components/calendar/Calendar.vue';

export default {
  name: 'AppointmentView',
  components: {
    ContentHeader,
    Calendar
  }
}
</script>

<style scoped></style>
