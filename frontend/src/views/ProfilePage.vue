<!-- frontend/src/views/ProfilePage.vue -->
<template>
  <div class="profile-container">
    <div class="container">
      <h1>Мой профиль</h1>

      <div class="tabs">
        <button
          @click="activeTab = 'info'"
          :class="['tab-button', { active: activeTab === 'info' }]"
        >
          Личная информация
        </button>
        <button
          @click="activeTab = 'registrations'"
          :class="['tab-button', { active: activeTab === 'registrations' }]"
        >
          Мои записи
        </button>
        <button
          v-if="canEditEvents"
          @click="activeTab = 'events'"
          :class="['tab-button', { active: activeTab === 'events' }]"
        >
          Мои мероприятия
        </button>
      </div>

      <!-- ТАБ 1: Личная информация -->
      <div v-if="activeTab === 'info'" class="tab-content">
        <div class="info-card card">
          <div class="info-row">
            <div class="info-field">
              <label>Имя</label>
              <p>{{ userData.first_name }}</p>
            </div>
            <div class="info-field">
              <label>Фамилия</label>
              <p>{{ userData.last_name }}</p>
            </div>
          </div>

          <div class="info-row">
            <div class="info-field">
              <label>Email</label>
              <p>{{ userData.email }}</p>
            </div>
            <div class="info-field">
              <label>Telegram</label>
              <p>{{ userData.telegram_alias || '—' }}</p>
            </div>
          </div>

          <div class="info-row">
            <div class="info-field">
              <label>Курс</label>
              <p>{{ userData.course ? userData.course + ' курс' : '—' }}</p>
            </div>
            <div class="info-field">
              <label>Группа</label>
              <p>{{ userData.group_name }}</p>
            </div>
          </div>

          <div v-if="userRole === 'admin' || userRole === 'starosta'" class="admin-badge">
            👑 {{ userRole === 'admin' ? 'Администратор' : 'Староста' }}
          </div>
        </div>
      </div>

      <!-- ТАБ 2: Мои записи -->
      <div v-if="activeTab === 'registrations'" class="tab-content">
        <div v-if="loadingReg" class="flex-center" style="min-height: 300px">
          <div class="spinner"></div>
        </div>

        <div v-else>
          <div v-if="errorReg" class="alert alert-error">
            ❌ {{ errorReg }}
          </div>

          <div v-if="registrations.length === 0" class="empty-state">
            <p>📭 Вы не записаны ни на одно мероприятие</p>
          </div>

          <div v-else class="registrations-list">
            <div v-for="reg in registrations" :key="reg.id" class="registration-item card">
              <div class="flex-between">
                <div>
                  <h3>{{ reg.title }}</h3>
                  <p class="reg-meta">
                    🕐 {{ reg.slot_time }} | 📍 {{ reg.group_name }}
                  </p>
                </div>
                <button @click="cancelRegistration(reg.id, reg.time_slot_id)" class="btn btn-danger btn-sm">
                  ❌ Отмена
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- ТАБ 3: Мои мероприятия (для админов и старост) -->
      <div v-if="activeTab === 'events' && canEditEvents" class="tab-content">
        <div v-if="loadingEvents" class="flex-center" style="min-height: 300px">
          <div class="spinner"></div>
        </div>

        <div v-else>
          <div v-if="errorEvents" class="alert alert-error">
            ❌ {{ errorEvents }}
          </div>

          <div v-if="userEvents.length === 0" class="empty-state">
            <p>📭 Вы не создали ни одного мероприятия</p>
          </div>

          <div v-else class="events-list">
            <div v-for="event in userEvents" :key="event.id" class="event-item card">
              <div class="flex-between">
                <div>
                  <h3>{{ event.title }}</h3>
                  <p class="event-meta">
                    🕐 {{ event.start_time }} - {{ event.end_time }} | 📍 {{ event.group_name }}
                  </p>
                </div>
                <div class="flex gap-8">
                  <button @click="editEventModal(event)" class="btn btn-secondary btn-sm">
                    ✏️ Редактировать
                  </button>
                  <button @click="deleteUserEvent(event.id)" class="btn btn-danger btn-sm">
                    🗑️ Удалить
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Модальное окно редактирования мероприятия -->
        <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
          <div class="modal">
            <div class="modal-header">
              <h3>Редактировать мероприятие</h3>
              <button @click="showEditModal = false" class="close-btn">✕</button>
            </div>

            <form @submit.prevent="updateUserEvent">
              <div class="input-group">
                <label class="input-label">Название</label>
                <input
                  v-model="editingEvent.title"
                  type="text"
                  class="input-field"
                  required
                />
              </div>

              <div class="form-row">
                <div class="input-group">
                  <label class="input-label">Начало (HH:MM)</label>
                  <input
                    v-model="editingEvent.start_time"
                    type="text"
                    class="input-field"
                    required
                  />
                </div>

                <div class="input-group">
                  <label class="input-label">Окончание (HH:MM)</label>
                  <input
                    v-model="editingEvent.end_time"
                    type="text"
                    class="input-field"
                    required
                  />
                </div>
              </div>

              <div class="input-group">
                <label class="input-label">Количество мест</label>
                <input
                  v-model.number="editingEvent.total_slots"
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
                <button type="button" class="btn btn-secondary" @click="showEditModal = false">
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
import { ref, onMounted, computed } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_URL } from '@/config';

export default {
  name: 'ProfilePage',
  setup() {
    const router = useRouter();
    const activeTab = ref('info');
    const userData = ref({});
    const userRole = ref('student');
    const registrations = ref([]);
    const userEvents = ref([]);
    const loadingReg = ref(false);
    const loadingEvents = ref(false);
    const errorReg = ref('');
    const errorEvents = ref('');
    const showEditModal = ref(false);
    const editLoading = ref(false);
    const editError = ref('');

    const editingEvent = ref({
      id: null,
      title: '',
      start_time: '',
      end_time: '',
      total_slots: null,
    });

    // 🔑 computed: проверяем может ли редактировать события
    const canEditEvents = computed(() => {
      return userRole.value === 'admin' || userRole.value === 'starosta';
    });

    onMounted(() => {
      const userDataStr = localStorage.getItem('user_data');
      if (!userDataStr) {
        router.push('/login');
        return;
      }

      userData.value = JSON.parse(userDataStr);
      userRole.value = userData.value.role || 'student';
      
      loadRegistrations();
      if (canEditEvents.value) {
        loadUserEvents();
      }
    });

    const loadRegistrations = async () => {
      loadingReg.value = true;
      errorReg.value = '';

      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.get(`${API_URL}/api/registrations/${userId}`);
        registrations.value = response.data.registrations;
      } catch (err) {
        errorReg.value = 'Ошибка при загрузке записей';
        console.error(err);
      } finally {
        loadingReg.value = false;
      }
    };

    const loadUserEvents = async () => {
      loadingEvents.value = true;
      errorEvents.value = '';

      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.get(`${API_URL}/api/events/organizer/${userId}`);
        userEvents.value = response.data.events;
      } catch (err) {
        errorEvents.value = 'Ошибка при загрузке мероприятий';
        console.error(err);
      } finally {
        loadingEvents.value = false;
      }
    };

    const cancelRegistration = async (registrationId, timeSlotId) => {
      if (!confirm('Вы уверены?')) return;

      try {
        const response = await axios.delete(
          `${API_URL}/api/registrations/${registrationId}/${timeSlotId}`
        );

        if (response.data.success) {
          loadRegistrations();
        }
      } catch (err) {
        console.error('❌ Ошибка при отмене:', err.response?.data || err);
        errorReg.value = err.response?.data?.detail || 'Ошибка при отмене записи';
      }
    };

    const editEventModal = (event) => {
      editingEvent.value = {
        id: event.id,
        title: event.title,
        start_time: event.start_time,
        end_time: event.end_time,
        total_slots: event.total_slots,
      };
      showEditModal.value = true;
    };

    const updateUserEvent = async () => {
      editError.value = '';
      editLoading.value = true;

      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.put(
          `${API_URL}/api/events/${editingEvent.value.id}?user_id=${userId}`,
          {
            title: editingEvent.value.title,
            start_time: editingEvent.value.start_time,
            end_time: editingEvent.value.end_time,
            total_slots: editingEvent.value.total_slots,
          }
        );

        if (response.data.success) {
          showEditModal.value = false;
          loadUserEvents();
        }
      } catch (err) {
        editError.value = err.response?.data?.detail || 'Ошибка при обновлении';
      } finally {
        editLoading.value = false;
      }
    };

    const deleteUserEvent = async (eventId) => {
      if (!confirm('Вы уверены, что хотите удалить это мероприятие?')) return;

      try {
        const userId = localStorage.getItem('user_id');
        const response = await axios.delete(
          `${API_URL}/api/events/${eventId}?user_id=${userId}`
        );

        if (response.data.success) {
          loadUserEvents();
        }
      } catch (err) {
        errorEvents.value = err.response?.data?.detail || 'Ошибка при удалении';
      }
    };

    return {
      activeTab,
      userData,
      userRole,
      registrations,
      userEvents,
      canEditEvents,
      loadingReg,
      loadingEvents,
      errorReg,
      errorEvents,
      showEditModal,
      editLoading,
      editError,
      editingEvent,
      cancelRegistration,
      editEventModal,
      updateUserEvent,
      deleteUserEvent,
    };
  },
};
</script>

<style scoped>
.profile-container {
  padding: 40px 0;
  min-height: 100vh;
}

.tabs {
  display: flex;
  gap: 24px;
  border-bottom: 1px solid var(--border-color);
  margin-bottom: 32px;
}

.tab-button {
  background: none;
  border: none;
  color: var(--text-secondary);
  font-weight: 600;
  padding: 12px 0;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.3s ease;
}

.tab-button.active {
  color: var(--primary-color);
  border-bottom-color: var(--primary-color);
}

.tab-button:hover {
  color: var(--primary-color);
}

.info-card {
  max-width: 600px;
}

.info-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
  margin-bottom: 24px;
}

.info-field {
  display: flex;
  flex-direction: column;
}

.info-field label {
  font-size: 12px;
  color: var(--text-secondary);
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 8px;
  letter-spacing: 0.5px;
}

.info-field p {
  font-size: 16px;
  color: var(--text-primary);
  margin: 0;
  font-weight: 500;
}

.admin-badge {
  background: linear-gradient(135deg, var(--primary-color), rgba(168, 85, 247, 0.7));
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  font-weight: 600;
  text-align: center;
  margin-top: 16px;
}

.registrations-list,
.events-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.registration-item,
.event-item {
  padding: 20px;
}

.registration-item h3,
.event-item h3 {
  margin: 0 0 8px 0;
}

.reg-meta,
.event-meta {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.empty-state {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
  font-size: 16px;
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

.flex-between {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
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
  .info-row {
    grid-template-columns: 1fr;
  }

  .registration-item,
  .event-item {
    flex-direction: column;
  }

  .flex-between {
    flex-direction: column;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
