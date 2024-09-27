import { createRouter, createWebHistory } from 'vue-router';
import AuthPage from '../components/AuthPage.vue';
import RegisterUser from '../components/RegisterUser.vue';

const routes = [
  {
    path: '/',
    name: 'Auth',
    component: AuthPage,
  },
  {
    path: '/app',
    name: 'App',
    component: () => import('../App.vue'),
  },
  {
    path: '/register',
    name: 'RegisterUser',
    component: RegisterUser,
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.VITE_APP_API_URL),
  routes,
});

// Add a global beforeEach navigation guard
router.beforeEach((to, from, next) => {
  const isAuthenticated = !!localStorage.getItem('token'); // Check if the user has a token

  // If trying to access /app and not authenticated, redirect to /
  if (to.name === 'App' && !isAuthenticated) {
    next({ name: 'Auth' });
  } else {
    next(); // Allow the navigation
  }
});

export default router;
