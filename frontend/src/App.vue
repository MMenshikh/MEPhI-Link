<!-- frontend/src/App.vue -->
<template>
  <div id="app">
    <Navigation v-if="showNavbar" />
    <router-view />
  </div>
</template>

<script>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Navigation from './components/Navigation.vue';

export default {
  name: 'App',
  components: { Navigation },
  setup() {
    const route = useRoute();

    // шапка НЕ показывается на /login и /register
    const showNavbar = computed(() => {
      return route.path !== '/login' && route.path !== '/register';
    });

    return { showNavbar };
  },
};
</script>

<style scoped>
#app {
  min-height: 100vh;
}
</style>
