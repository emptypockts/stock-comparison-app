import { createRouter, createWebHistory } from 'vue-router';
import AuthPage from '../components/AuthPage.vue';
import RegisterUser from '../components/RegisterUser.vue';
import AI from '../components/AI.vue';
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
  {
    path: '/ai',
    name: 'AI',
    component: AI,
  },
];


const router = createRouter({
  history: createWebHistory(),
  routes,
});

console.log("router variable", router)
// async function verifyToken() {
//   const token = localStorage.getItem('token');
//   if (!token) return false; // No token exists

//   try {
//     const response = await axios.post('/api/verify', {}, {
//       headers: {
//         'token': token,
//       },
//     });
//     return response.data.success; // Return true if token is valid, false otherwise
//   } catch (error) {
//     console.error('Token verification error:', error.response ? error.response.data.message : error.message);
//     return false;
//   }
// }

// // Add a global beforeEach navigation guard
// router.beforeEach(async (to, from, next) => {
//   const isAuthenticated = await verifyToken(); // Check if the user has a token

//   // If trying to access /app and not authenticated, redirect to /
//   if (to.name === 'App' && !isAuthenticated) {
//     console.log("Removing token and expiration")
//     localStorage.removeItem('token'); // Remove the expired token from localStorage
//     localStorage.removeItem('tokenExpiration')
//     next({ name: 'Auth' });
//   } else {
//     next(); // Allow the navigation
//   }
// });

export default router;
