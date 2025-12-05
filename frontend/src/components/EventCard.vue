<!-- frontend/src/components/EventCard.vue -->
<template>
  <div class="event-card card">
    <h3>{{ event.title }}</h3>
    <p class="event-time">
      🕐 {{ event.start_time }} - {{ event.end_time }}
    </p>
    <p class="event-group">
      📍 {{ event.group_name }}
    </p>

    <button @click="$emit('view', event.id)" class="btn btn-primary" style="width: 100%; margin-top: 16px">
      Перейти
    </button>
  </div>
</template>

<script>
import { API_URL } from '@/config';

export default {
  name: 'EventCard',
  props: {
    event: {
      type: Object,
      required: true,
    },
  },
  emits: ['view'],
};
</script>

<style scoped>
.event-card {
  cursor: pointer;
}

.event-card h3 {
  margin-top: 0;
  color: var(--text-primary);
}

.event-time,
.event-group {
  margin: 8px 0;
  color: var(--text-secondary);
  font-size: 14px;
}
</style>
