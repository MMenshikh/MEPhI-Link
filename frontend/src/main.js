// frontend/src/main.js
import { createApp } from 'vue';
import { createRouter, createWebHistory } from 'vue-router';
import App from './App.vue';
import routes from './router';
import './assets/styles/main.css';

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// Protect routes
router.beforeEach((to, from, next) => {
  const isLoggedIn = !!localStorage.getItem('user_id');
  const publicPages = ['/login', '/register'];
  const authRequired = !publicPages.includes(to.path);

  if (authRequired && !isLoggedIn) {
    next('/login');
  } else if ((to.path === '/login' || to.path === '/register') && isLoggedIn) {
    next('/dashboard');
  } else {
    next();
  }
});

const app = createApp(App);
app.use(router);
app.mount('#app');
