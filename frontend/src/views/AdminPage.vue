<!-- frontend/src/views/AdminPage.vue -->
<template>
  <div class="admin-container">
    <div class="container">
      <h1>Админ-панель</h1>

      <div class="tabs">
        <button
          @click="activeTab = 'users'"
          :class="['tab-button', { active: activeTab === 'users' }]"
        >
          Пользователи
        </button>
      </div>

      <!-- ТАБ: Управление пользователями -->
      <div v-if="activeTab === 'users'" class="tab-content">
        <div v-if="loading" class="flex-center" style="min-height: 300px">
          <div class="spinner"></div>
        </div>

        <div v-else>
          <div v-if="error" class="alert alert-error">
            ❌ {{ error }}
          </div>

          <div class="users-table">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Имя</th>
                  <th>Фамилия</th>
                  <th>Email</th>
                  <th>Группа</th>
                  <th>Роль</th>
                  <th>Действия</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="user in users" :key="user.id">
                  <td>#{{ user.id }}</td>
                  <td>{{ user.first_name }}</td>
                  <td>{{ user.last_name }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.group_name }}</td>
                  <td>
                    <select 
                      :value="user.role || 'student'" 
                      @change="changeUserRole(user.id, $event.target.value)"
                      class="role-select"
                    >
                      <option value="student">Студент</option>
                      <option value="starosta">Староста</option>
                      <option value="admin">Админ</option>
                    </select>
                  </td>
                  <td class="actions-cell">
                    <button
                      @click="deleteUser(user.id)"
                      class="btn btn-danger btn-sm"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_URL } from '@/config';

export default {
  name: 'AdminPage',
  setup() {
    const router = useRouter();
    const activeTab = ref('users');
    const users = ref([]);
    const loading = ref(true);
    const error = ref('');

    onMounted(() => {
      const userData = JSON.parse(localStorage.getItem('user_data') || '{}');
      
      if (userData.role !== 'admin') {
        router.push('/dashboard');
        return;
      }
      
      loadUsers();
    });

    const loadUsers = async () => {
      try {
        const adminId = localStorage.getItem('user_id');
        const response = await axios.get(`${API_URL}/api/admin/users?admin_id=${adminId}`);
        users.value = response.data.users;
        error.value = '';
      } catch (err) {
        error.value = 'Ошибка при загрузке пользователей';
        console.error(err);
      } finally {
        loading.value = false;
      }
    };

    const changeUserRole = async (userId, newRole) => {
      if (!confirm(`Вы уверены, что хотите изменить роль пользователя на "${newRole}"?`)) {
        return;
      }

      try {
        const adminId = localStorage.getItem('user_id');
        const response = await axios.post(
          `${API_URL}/api/admin/make-admin?admin_id=${adminId}`,
          { user_id: userId, role: newRole }
        );

        if (response.data.success) {
          loadUsers();
          console.log('✅ Роль изменена:', response.data.message);
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при изменении роли';
        console.error('❌ Ошибка:', err);
      }
    };

    const deleteUser = async (userId) => {
      if (!confirm('Вы уверены, что хотите удалить этого пользователя?')) {
        return;
      }

      try {
        const adminId = localStorage.getItem('user_id');
        const response = await axios.delete(
          `${API_URL}/api/admin/users/${userId}?admin_id=${adminId}`
        );

        if (response.data.success) {
          loadUsers();
          console.log('✅ Пользователь удалён');
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при удалении пользователя';
        console.error('❌ Ошибка:', err);
      }
    };

    return {
      activeTab,
      users,
      loading,
      error,
      changeUserRole,
      deleteUser,
    };
  },
};
</script>

<style scoped>
.admin-container {
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

.users-table {
  background-color: var(--bg-dark-2);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead {
  background-color: rgba(168, 85, 247, 0.1);
  border-bottom: 2px solid var(--border-color);
}

th {
  padding: 16px;
  text-align: left;
  font-weight: 600;
  color: var(--text-primary);
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

td {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  color: var(--text-primary);
  font-size: 14px;
}

tbody tr:hover {
  background-color: rgba(168, 85, 247, 0.05);
}

.role-select {
  background-color: var(--bg-dark);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.role-select:hover {
  border-color: var(--primary-color);
}

.role-select:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(168, 85, 247, 0.2);
}

.actions-cell {
  display: flex;
  gap: 8px;
}

.alert {
  padding: 16px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.alert-error {
  background-color: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #ef4444;
}

.flex-center {
  display: flex;
  align-items: center;
  justify-content: center;
}

@media (max-width: 768px) {
  .users-table {
    overflow-x: auto;
  }

  table {
    font-size: 12px;
  }

  th,
  td {
    padding: 12px;
  }

  .role-select {
    padding: 6px 8px;
    font-size: 12px;
  }

  .actions-cell {
    flex-direction: column;
    gap: 4px;
  }
}
</style>
