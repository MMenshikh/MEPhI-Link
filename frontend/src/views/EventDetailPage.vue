<!-- frontend/src/views/EventDetailPage.vue -->
<template>
  <div class="event-detail-container">
    <div class="container">
      <router-link to="/dashboard" class="back-link">← Вернуться</router-link>

      <div v-if="loading" class="flex-center" style="min-height: 400px">
        <div class="spinner"></div>
      </div>

      <div v-else>
        <div v-if="error" class="alert alert-error">
          ❌ {{ error }}
        </div>

        <div v-if="Object.keys(event).length > 0" class="event-detail">
          <div class="event-header">
            <div>
              <h1>{{ event.title }}</h1>
              <p class="event-meta">
                🕐 {{ event.start_time }} - {{ event.end_time }} | 📍 {{ event.group_name }}
              </p>
            </div>
            <div v-if="isOrganizer" class="flex gap-8">
              <button @click="showEditEvent = true" class="btn btn-secondary btn-sm">
                ✏️ Редактировать
              </button>
              <button @click="deleteEvent" class="btn btn-danger btn-sm">
                🗑️ Удалить
              </button>
            </div>
          </div>

          <!-- Список слотов для записи -->
          <div class="slots-section">
            <h2>Доступные слоты</h2>
            <div class="slots-grid">
              <button
                v-for="slot in slots"
                :key="slot.id"
                @click="selectSlot(slot)"
                :class="['slot-button', { selected: selectedSlot?.id === slot.id, unavailable: !slot.is_available }]"
                :disabled="!slot.is_available || hasRegistration"
              >
                {{ slot.slot_time }}
                <span v-if="!slot.is_available" class="unavailable-badge">Занято</span>
              </button>
            </div>

            <div v-if="selectedSlot && !hasRegistration" class="registration-action">
              <button @click="registerForSlot" class="btn btn-primary" :disabled="regLoading">
                <span v-if="regLoading" class="spinner"></span>
                <span v-else>✅ Подтвердить запись на {{ selectedSlot.slot_time }}</span>
              </button>
            </div>

            <div v-if="hasRegistration" class="alert alert-info">
              ✅ Вы уже записаны на это мероприятие на слот <strong>{{ userRegistrationTime }}</strong>
            </div>
          </div>
        </div>

        <!-- Модальное окно редактирования мероприятия -->
        <div v-if="showEditEvent" class="modal-overlay" @click.self="showEditEvent = false">
          <div class="modal">
            <div class="modal-header">
              <h3>Редактировать мероприятие</h3>
              <button @click="showEditEvent = false" class="close-btn">✕</button>
            </div>

            <form @submit.prevent="updateEvent">
              <div class="input-group">
                <label class="input-label">Название</label>
                <input
                  v-model="editEvent.title"
                  type="text"
                  class="input-field"
                  required
                />
              </div>

              <div class="form-row">
                <div class="input-group">
                  <label class="input-label">Начало (HH:MM)</label>
                  <input
                    v-model="editEvent.start_time"
                    type="text"
                    class="input-field"
                    required
                  />
                </div>

                <div class="input-group">
                  <label class="input-label">Окончание (HH:MM)</label>
                  <input
                    v-model="editEvent.end_time"
                    type="text"
                    class="input-field"
                    required
                  />
                </div>
              </div>

              <div class="input-group">
                <label class="input-label">Количество мест</label>
                <input
                  v-model.number="editEvent.total_slots"
                  type="number"
                  class="input-field"
                  required
                />
              </div>

              <div v-if="editError" class="alert alert-error">
                ❌ {{ editError }}
              </div>

              <div class="flex gap-8">
                <button type="submit" class="btn btn-primary" :disabled="editLoading">
                  <span v-if="editLoading" class="spinner"></span>
                  <span v-else>Сохранить</span>
                </button>
                <button type="button" class="btn btn-secondary" @click="showEditEvent = false">
                  Отмена
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import axios from 'axios';
import { API_URL } from '@/config';

export default {
  name: 'EventDetailPage',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const eventId = route.params.id;

    const event = ref({});
    const slots = ref([]);
    const loading = ref(true);
    const error = ref('');
    const regLoading = ref(false);
    const selectedSlot = ref(null);
    const hasRegistration = ref(false);
    const userRegistrationTime = ref('');
    const isOrganizer = ref(false);
    const showEditEvent = ref(false);
    const editLoading = ref(false);
    const editError = ref('');

    const editEvent = ref({
      title: '',
      start_time: '',
      end_time: '',
      total_slots: null,
    });

    onMounted(() => {
      const userData = localStorage.getItem('user_data');
      if (!userData) {
        router.push('/login');
        return;
      }

      loadEvent();
      checkUserRegistration();
    });

    const loadEvent = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/events/${eventId}`);
        event.value = response.data.event;
        slots.value = response.data.slots;

        editEvent.value = {
          title: event.value.title,
          start_time: event.value.start_time,
          end_time: event.value.end_time,
          total_slots: event.value.total_slots,
        };
      } catch (err) {
        error.value = 'Ошибка при загрузке мероприятия';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const checkUserRegistration = async () => {
      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.get(`${API_URL}/api/registrations/${userId}`);
        
        const registration = response.data.registrations.find(r => r.event_id === parseInt(eventId));
        if (registration) {
          hasRegistration.value = true;
          userRegistrationTime.value = registration.slot_time;
        }
      } catch (err) {
        console.error(err);
      }
    };

    const selectSlot = (slot) => {
      if (slot.is_available && !hasRegistration.value) {
        selectedSlot.value = selectedSlot.value?.id === slot.id ? null : slot;
      }
    };

    const registerForSlot = async () => {
      if (!selectedSlot.value) return;

      regLoading.value = true;
      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.post(
          `${API_URL}/api/registrations?user_id=${userId}&event_id=${eventId}&time_slot_id=${selectedSlot.value.id}`
        );

        if (response.data.success) {
          hasRegistration.value = true;
          userRegistrationTime.value = selectedSlot.value.slot_time;
          selectedSlot.value = null;
          loadEvent();
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при записи';
      } finally {
        regLoading.value = false;
      }
    };

    const updateEvent = async () => {
      editError.value = '';
      editLoading.value = true;

      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.put(
          `${API_URL}/api/events/${eventId}?user_id=${userId}`,
          {
            title: editEvent.value.title,
            start_time: editEvent.value.start_time,
            end_time: editEvent.value.end_time,
            total_slots: editEvent.value.total_slots,
          }
        );

        if (response.data.success) {
          showEditEvent.value = false;
          loadEvent();
        }
      } catch (err) {
        editError.value = err.response?.data?.detail || 'Ошибка при обновлении';
      } finally {
        editLoading.value = false;
      }
    };

    const deleteEvent = async () => {
      if (!confirm('Вы уверены, что хотите удалить это мероприятие?')) return;

      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.delete(
          `${API_URL}/api/events/${eventId}?user_id=${userId}`
        );

        if (response.data.success) {
          router.push('/dashboard');
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при удалении';
      }
    };

    return {
      event,
      slots,
      loading,
      error,
      regLoading,
      selectedSlot,
      hasRegistration,
      userRegistrationTime,
      isOrganizer,
      showEditEvent,
      editLoading,
      editError,
      editEvent,
      selectSlot,
      registerForSlot,
      updateEvent,
      deleteEvent,
    };
  },
};
</script>

<style scoped>
.event-detail-container {
  padding: 40px 0;
  min-height: 100vh;
}

.back-link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
  margin-bottom: 24px;
  display: inline-block;
  transition: all 0.3s ease;
}

.back-link:hover {
  color: var(--secondary-color);
}

.event-detail {
  background-color: var(--bg-dark-2);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  padding: 32px;
  margin-bottom: 32px;
}

.event-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  padding-bottom: 24px;
  border-bottom: 1px solid var(--border-color);
}

.event-header h1 {
  margin-bottom: 8px;
}

.event-meta {
  color: var(--text-secondary);
  font-size: 14px;
}

.slots-section {
  margin-top: 32px;
}

.slots-section h2 {
  margin-bottom: 16px;
}

.slots-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  gap: 12px;
  margin-bottom: 24px;
}

.slot-button {
  padding: 12px 8px;
  background-color: var(--bg-dark);
  border: 2px solid var(--border-color);
  border-radius: 8px;
  color: var(--text-primary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 14px;
  font-weight: 600;
  position: relative;
}

.slot-button:hover:not(.unavailable):not(:disabled) {
  border-color: var(--primary-color);
  background-color: rgba(168, 85, 247, 0.1);
}

.slot-button.selected {
  background-color: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

.slot-button.unavailable {
  opacity: 0.5;
  cursor: not-allowed;
}

.slot-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.unavailable-badge {
  display: block;
  font-size: 10px;
  margin-top: 4px;
  opacity: 0.7;
}

.registration-action {
  margin-top: 24px;
}

.registration-action button {
  width: 100%;
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

@media (max-width: 768px) {
  .event-header {
    flex-direction: column;
    gap: 16px;
  }

  .slots-grid {
    grid-template-columns: repeat(auto-fill, minmax(60px, 1fr));
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
