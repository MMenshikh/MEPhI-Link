// frontend/src/router.js
import LoginPage from './views/LoginPage.vue';
import RegisterPage from './views/RegisterPage.vue';
import DashboardPage from './views/DashboardPage.vue';
import ProfilePage from './views/ProfilePage.vue';
import EventDetailPage from './views/EventDetailPage.vue';
import AdminPage from './views/AdminPage.vue';

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', component: LoginPage },
  { path: '/register', component: RegisterPage },
  { path: '/dashboard', component: DashboardPage },
  { path: '/profile', component: ProfilePage },
  { path: '/event/:id', component: EventDetailPage },
  { path: '/admin', component: AdminPage },
  { path: '/:pathMatch(.*)*', redirect: '/dashboard' },
];

export default routes;
