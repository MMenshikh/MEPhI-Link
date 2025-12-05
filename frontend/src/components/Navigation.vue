<!-- frontend/src/components/Navigation.vue -->
<template>
  <nav class="navbar">
    <div class="container flex-between">
      <div class="flex gap-16">
        <router-link to="/dashboard" class="navbar-brand">
          MEPhI-Link
        </router-link>
        <ul class="nav-links">
          <li>
            <router-link to="/dashboard" :class="{ active: isActive('/dashboard') }">
              Мероприятия
            </router-link>
          </li>
          <li>
            <router-link to="/profile" :class="{ active: isActive('/profile') }">
              Профиль
            </router-link>
          </li>
          <li v-if="userRole === 'admin'">
            <router-link to="/admin" :class="{ active: isActive('/admin') }">
              Админ-панель
            </router-link>
          </li>
        </ul>
      </div>
      
      <!-- 🔑 ДОБАВИТЬ: Имя Фамилия и Выход -->
      <div class="navbar-user">
        <span v-if="userName" class="user-name">
          👤 {{ userName }}
        </span>
        <button @click="logout" class="btn btn-secondary btn-sm">
          Выход
        </button>
      </div>
    </div>
  </nav>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

export default {
  name: 'Navigation',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const userRole = ref('student');
    const userName = ref('');

    onMounted(() => {
      const userData = localStorage.getItem('user_data');
      if (userData) {
        const user = JSON.parse(userData);
        userRole.value = user.role || 'student';
        
        // 🔑 ДОБАВИТЬ: Сохраняем имя и фамилию
        if (user.first_name && user.last_name) {
          userName.value = `${user.first_name} ${user.last_name}`;
        }
      }
    });

    const logout = () => {
      localStorage.removeItem('user_id');
      localStorage.removeItem('user_data');
      router.push('/login');
    };

    const isActive = (path) => {
      return route.path === path;
    };

    return {
      logout,
      isActive,
      userRole,
      userName,
    };
  },
};
</script>

<style scoped>
.navbar {
  background-color: var(--bg-dark-2);
  border-bottom: 1px solid var(--border-color);
  padding: 16px 0;
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  font-size: 20px;
  font-weight: 700;
  background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-decoration: none;
}

.nav-links {
  list-style: none;
  display: flex;
  gap: 24px;
  margin: 0;
  padding: 0;
}

.nav-links a {
  color: var(--text-secondary);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-links a:hover,
.nav-links a.active {
  color: var(--primary-color);
}

/* 🔑 НОВЫЕ СТИЛИ */
.navbar-user {
  display: flex;
  gap: 16px;
  align-items: center;
  white-space: nowrap;
}

.user-name {
  color: var(--text-secondary);
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .navbar-user {
    gap: 8px;
  }

  .user-name {
    display: none;
  }

  .nav-links {
    gap: 12px;
  }
}
</style>
