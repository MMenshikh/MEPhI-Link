<!-- frontend/src/views/DashboardPage.vue -->
<template>
  <div class="dashboard-container">
    <div class="container">
      <div class="dashboard-header">
        <h1>Мероприятия</h1>
        <button 
          v-if="canCreateEvent" 
          @click="showCreateEvent = true" 
          class="btn btn-primary"
        >
          ➕ Создать мероприятие
        </button>
      </div>

      <div v-if="loading" class="flex-center" style="min-height: 400px">
        <div class="spinner"></div>
      </div>

      <div v-else>
        <div v-if="error" class="alert alert-error">
          ❌ {{ error }}
        </div>

        <div v-if="events.length === 0" class="empty-state">
          <p>📭 Нет доступных мероприятий</p>
        </div>

        <div v-else class="grid">
          <EventCard
            v-for="event in events"
            :key="event.id"
            :event="event"
            @view="viewEvent"
          />
        </div>
      </div>

      <!-- Модальное окно создания мероприятия -->
      <div v-if="showCreateEvent" class="modal-overlay" @click.self="showCreateEvent = false">
        <div class="modal">
          <div class="modal-header">
            <h3>Создать мероприятие</h3>
            <button @click="showCreateEvent = false" class="close-btn">✕</button>
          </div>

          <form @submit.prevent="createEvent">
            <div class="input-group">
              <label class="input-label">Название</label>
              <input
                v-model="newEvent.title"
                type="text"
                class="input-field"
                placeholder="Сдача лаб. работ по функ. анализу"
                required
              />
            </div>

            <div class="form-row">
              <div class="input-group">
                <label class="input-label">Начало (HH:MM)</label>
                <input
                  v-model="newEvent.start_time"
                  type="text"
                  class="input-field"
                  placeholder="09:00"
                  required
                />
              </div>

              <div class="input-group">
                <label class="input-label">Окончание (HH:MM)</label>
                <input
                  v-model="newEvent.end_time"
                  type="text"
                  class="input-field"
                  placeholder="14:30"
                  required
                />
              </div>
            </div>

            <div class="input-group">
              <label class="input-label">Количество мест</label>
              <input
                v-model.number="newEvent.total_slots"
                type="number"
                class="input-field"
                placeholder="30"
                required
              />
            </div>

            <div v-if="createError" class="alert alert-error">
              ❌ {{ createError }}
            </div>

            <div class="flex gap-8">
              <button type="submit" class="btn btn-primary" :disabled="createLoading">
                <span v-if="createLoading" class="spinner"></span>
                <span v-else>Создать</span>
              </button>
              <button type="button" class="btn btn-secondary" @click="showCreateEvent = false">
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import EventCard from '../components/EventCard.vue';
import { API_URL } from '@/config';

export default {
  name: 'DashboardPage',
  components: {
    EventCard,
  },
  setup() {
    const router = useRouter();
    const events = ref([]);
    const loading = ref(true);
    const error = ref('');
    const showCreateEvent = ref(false);
    const createLoading = ref(false);
    const createError = ref('');
    const userData = ref(null);

    const newEvent = ref({
      title: '',
      start_time: '',
      end_time: '',
      total_slots: null,
    });

    // 🔑 computed: проверяем role старосты или админа
    const canCreateEvent = computed(() => {
      if (!userData.value) return false;
      return userData.value.role === 'admin' || userData.value.role === 'starosta';
    });

    onMounted(() => {
      const userDataJSON = localStorage.getItem('user_data');
      if (!userDataJSON) {
        router.push('/login');
        return;
      }

      userData.value = JSON.parse(userDataJSON);
      loadEvents();
    });

    const loadEvents = async () => {
      try {
        const response = await axios.get(
          `${API_URL}/api/events/group/${userData.value.group_name}`
        );
        events.value = response.data.events;
      } catch (err) {
        error.value = 'Ошибка при загрузке мероприятий';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const createEvent = async () => {
      createError.value = '';

      if (!newEvent.value.title || !newEvent.value.start_time || !newEvent.value.end_time) {
        createError.value = 'Все поля обязательны';
        return;
      }

      createLoading.value = true;

      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.post(
          `${API_URL}/api/events?user_id=${userId}`,
          {
            title: newEvent.value.title,
            start_time: newEvent.value.start_time,
            end_time: newEvent.value.end_time,
            total_slots: newEvent.value.total_slots,
          }
        );

        if (response.data.success) {
          showCreateEvent.value = false;
          newEvent.value = {
            title: '',
            start_time: '',
            end_time: '',
            total_slots: null,
          };
          loadEvents();
        }
      } catch (err) {
        createError.value = err.response?.data?.detail || 'Ошибка при создании';
        console.error('Create event error:', err);
      } finally {
        createLoading.value = false;
      }
    };

    const viewEvent = (eventId) => {
      router.push(`/event/${eventId}`);
    };

    return {
      events,
      loading,
      error,
      showCreateEvent,
      createLoading,
      createError,
      canCreateEvent,
      newEvent,
      createEvent,
      viewEvent,
    };
  },
};
</script>

<style scoped>
.dashboard-container {
  padding: 40px 0;
  min-height: 100vh;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 32px;
}

.dashboard-header h1 {
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 80px 20px;
  color: var(--text-secondary);
  font-size: 18px;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal {
  background-color: var(--bg-dark-2);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px;
  max-width: 500px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.modal-header h3 {
  margin: 0;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-size: 24px;
  cursor: pointer;
  padding: 0;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s ease;
}

.close-btn:hover {
  color: var(--primary-color);
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.alert {
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.flex {
  display: flex;
}

.gap-8 {
  gap: 8px;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 16px;
    align-items: flex-start;
  }

  .modal {
    padding: 24px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
