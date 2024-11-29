import { createRouter, createWebHistory } from 'vue-router';
import AuthPage from '../components/AuthPage.vue';
import RegisterUser from '../components/RegisterUser.vue';
import AI from '../components/AI.vue';
import EconomyStats from '@/components/EconomyStats.vue';
import StockChart from '@/components/StockChart.vue';
import App from '@/App.vue';
import QtrStockTrend from '@/components/QtrStockTrend.vue';

const routes = [
  {
    path: '/',
    name: 'Auth',
    component: AuthPage,
  },
  {
    path: '/app',
    name: 'app',
    component: App,
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
  {
    path: '/economyidx',
    name: 'EconomyStats',
    component: EconomyStats,
  },
  {
    path: '/stockchart',
    name: 'StockChart',
    component: StockChart,
  },
  {
    path:'/qtrtrend',
    name:'qtrTrend',
    component:QtrStockTrend
  },
];



const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const isAuthenticated = localStorage.getItem('token'); // Example auth check
  if (to.name !== 'Auth' && !isAuthenticated) (next({ name: 'Auth' }),console.log("Token is not valid"));
  else next();
}),

{
  path: '/:catchAll(.*)',
  name: 'NotFound',
  component: () => import('@/components/NotFound.vue'), // Add a 404 page component if you have one
};

export default router;
