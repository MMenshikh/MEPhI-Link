<!-- frontend/src/views/LoginPage.vue -->
<template>
  <div class="login-container">
    <div class="login-box">
      <h1>MEPhI-Link</h1>
      <p class="subtitle">Агрегатор учебных сервисов</p>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label class="input-label">Email</label>
          <input
            v-model="email"
            type="email"
            class="input-field"
            placeholder="example@mail.com"
            required
          />
        </div>

        <div class="input-group">
          <label class="input-label">Пароль</label>
          <input
            v-model="password"
            type="password"
            class="input-field"
            placeholder="••••••••"
            required
          />
        </div>

        <div v-if="error" class="alert alert-error">
          ❌ {{ error }}
        </div>

        <button type="submit" class="btn btn-primary" :disabled="loading">
          <span v-if="loading" class="spinner"></span>
          <span v-else>Войти</span>
        </button>
      </form>

      <p class="text-center">
        Нет аккаунта?
        <router-link to="/register" class="link">Зарегистрироваться</router-link>
      </p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';
import { API_URL } from '@/config';


export default {
  name: 'LoginPage',
  setup() {
    const router = useRouter();
    const email = ref('');
    const password = ref('');
    const error = ref('');
    const loading = ref(false);

    const handleLogin = async () => {
      error.value = '';
      loading.value = true;

      try {
        const response = await axios.post(`${API_URL}/api/auth/login`, {
          email: email.value,
          password: password.value,
        });

        if (response.data.success) {
          localStorage.setItem('user_id', response.data.user_id);
          localStorage.setItem('user_data', JSON.stringify({
            id: response.data.user_id,
            first_name: response.data.first_name,
            last_name: response.data.last_name,
            email: response.data.email,
            group_name: response.data.group_name,
            is_admin: response.data.is_admin,
            role: response.data.role,
            course: response.data.course,
            telegram_alias: response.data.telegram_alias
          }));

          router.push('/dashboard');
        }
      } catch (err) {
        error.value = err.response?.data?.detail || 'Ошибка при входе';
      } finally {
        loading.value = false;
      }
    };

    return {
      email,
      password,
      error,
      loading,
      handleLogin,
    };
  },
};
</script>

<style scoped>
.login-container {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 100vh;
  background-color: var(--bg-dark);
}

.login-box {
  width: 100%;
  max-width: 400px;
  padding: 40px;
  background-color: var(--bg-dark-2);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
}

h1 {
  text-align: center;
  font-size: 28px;
  margin-bottom: 8px;
}

.subtitle {
  text-align: center;
  color: var(--text-secondary);
  font-size: 14px;
  margin-bottom: 32px;
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
  transition: all 0.3s ease;
}

.link:hover {
  color: var(--secondary-color);
}

button[type="submit"] {
  width: 100%;
}

@media (max-width: 480px) {
  .login-box {
    padding: 24px;
    border-radius: 12px;
  }

  h1 {
    font-size: 24px;
  }
}
</style>
