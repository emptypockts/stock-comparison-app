import { createRouter, createWebHistory } from 'vue-router';
import AuthPage from '@/views/AuthPage.vue';
import RegisterUser from '@/views/RegisterUser.vue';
import AI from '@/views/AI.vue';
import EconomyStats from '@/views/EconomyStats.vue';
import StockChart from '@/views/StockChart.vue';
import App from '@/App.vue';
import QtrStockTrend from '@/views/QtrStockTrend.vue';
import { verifyToken } from '@/utils/auth';



const router = createRouter({
  history:createWebHistory(),
  routes:[
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
  {
  path: '/:catchAll(.*)',
  name: 'NotFound',
  component: () => import('@/components/NotFound.vue')
  }
]
});

router.beforeEach(async (to, from) => {
  const token = localStorage.getItem('token');
  const isAuthenticated = verifyToken(token);
  if (to.name !== 'Auth' && to.name !== 'RegisterUser'&&!isAuthenticated){ 
    return {name:'Auth'}
    }
});


export default router;