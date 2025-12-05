<!-- frontend/src/views/RegisterPage.vue -->
<template>
  <div class="register-container">
    <div class="register-box">
      <h2>Регистрация</h2>

      <form @submit.prevent="handleRegister">
        <div class="form-row">
          <div class="input-group">
            <label class="input-label">Имя</label>
            <input
              v-model="formData.first_name"
              type="text"
              class="input-field"
              placeholder="Иван"
              required
            />
          </div>

          <div class="input-group">
            <label class="input-label">Фамилия</label>
            <input
              v-model="formData.last_name"
              type="text"
              class="input-field"
              placeholder="Петров"
              required
            />
          </div>
        </div>

        <div class="input-group">
          <label class="input-label">Email</label>
          <input
            v-model="formData.email"
            type="email"
            class="input-field"
            placeholder="example@mail.com"
            required
          />
        </div>

        <div class="input-group">
          <label class="input-label">Telegram alias</label>
          <input
            v-model="formData.telegram_alias"
            type="text"
            class="input-field"
            placeholder="@yourusername"
            required
          />
        </div>

        <div class="form-row">
          <div class="input-group">
            <label class="input-label">Курс</label>
            <select v-model="formData.course" class="input-field" required>
              <option value="">Выберите курс</option>
              <option value="1">1 курс</option>
              <option value="2">2 курс</option>
              <option value="3">3 курс</option>
              <option value="4">4 курс</option>
              <option value="5">5 курс</option>
            </select>
          </div>

          <div class="input-group">
            <label class="input-label">Группа</label>
            <select v-model="formData.group_name" class="input-field" required>
              <option value="">Выберите группу</option>
              <option v-for="group in groups" :key="group" :value="group">
                {{ group }}
              </option>
            </select>
          </div>
        </div>

        <div class="form-row">
          <div class="input-group">
            <label class="input-label">Пароль</label>
            <input
              v-model="formData.password"
              type="password"
              class="input-field"
              placeholder="••••••••"
              required
            />
          </div>

          <div class="input-group">
            <label class="input-label">Подтвердить пароль</label>
            <input
              v-model="formData.confirm_password"
              type="password"
              class="input-field"
              placeholder="••••••••"
              required
            />
          </div>
        </div>

        <div v-if="error" class="alert alert-error">
          ❌ {{ error }}
        </div>

        <div v-if="success" class="alert alert-success">
          ✅ {{ success }}
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Зарегистрироваться</span>
        </button>
      </form>

      <p class="text-center">
        Уже есть аккаунт?
        <router-link to="/login" class="link">Войти</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_URL } from '@/config';


export default {
  name: 'RegisterPage',
  setup() {
    const router = useRouter();
    const formData = ref({
      first_name: '',
      last_name: '',
      email: '',
      password: '',
      confirm_password: '',
      telegram_alias: '',
      course: '',
      group_name: '',
    });
    const groups = ref([]);
    const error = ref('');
    const success = ref('');
    const loading = ref(false);

    onMounted(async () => {
      try {
        const response = await axios.get(`${API_URL}/api/groups`);
        groups.value = response.data.groups;
      } catch (err) {
        console.error('Ошибка при загрузке групп:', err);
      }
    });

    const handleRegister = async () => {
      error.value = '';
      success.value = '';

      // Валидация
      if (formData.value.password !== formData.value.confirm_password) {
        error.value = '❌ Пароли не совпадают';
        return;
      }

      if (formData.value.password.length < 6) {
        error.value = '❌ Пароль должен быть минимум 6 символов';
        return;
      }

      loading.value = true;

      try {
        const response = await axios.post(`${API_URL}/api/auth/register`, {
          first_name: formData.value.first_name,
          last_name: formData.value.last_name,
          email: formData.value.email,
          password: formData.value.password,
          telegram_alias: formData.value.telegram_alias,
          course: parseInt(formData.value.course),
          group_name: formData.value.group_name,
        });

        if (response.data.success) {
          success.value = '✅ Регистрация успешна! Перенаправляем на логин...';
          setTimeout(() => {
            router.push('/login');
          }, 2000);
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при регистрации';
      } finally {
        loading.value = false;
      }
    };

    return {
      formData,
      groups,
      error,
      success,
      loading,
      handleRegister,
    };
  },
};
</script>

<style scoped>
.register-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--bg-dark);
  padding: 20px 0;
}

.register-box {
  width: 100%;
  max-width: 600px;
  padding: 40px;
  background-color: var(--bg-dark-2);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

h2 {
  text-align: center;
  margin-bottom: 32px;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

form {
  margin-bottom: 24px;
}

.text-center {
  text-align: center;
  font-size: 14px;
  color: var(--text-secondary);
}

.link {
  color: var(--primary-color);
  text-decoration: none;
  font-weight: 600;
}

.link:hover {
  color: var(--secondary-color);
}

button[type="submit"] {
  width: 100%;
}

@media (max-width: 480px) {
  .register-box {
    padding: 24px;
  }

  .form-row {
    grid-template-columns: 1fr;
  }
}
</style>
