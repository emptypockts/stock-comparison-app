import { createRouter, createWebHistory } from 'vue-router';
import AuthPage from '@/views/AuthPage.vue';
import RegisterUser from '@/views/RegisterUser.vue';
import AI from '@/views/AI.vue';
import EconomyStats from '@/views/EconomyStats.vue';
import StockChart from '@/views/StockChart.vue';
import MainLayout from '@/views/MainLayout.vue';
import QtrStockTrend from '@/views/QtrStockTrend.vue';
import { verifyToken } from '@/utils/auth';
import App from '@/layouts/App.vue';


const router = createRouter({
  history:createWebHistory(),
  routes:[
  {
    path: '/',
    name: 'Auth',
    component: AuthPage,
  },
  {
    path: '/dashboard',
    component: App,
    children:[
        {
    path: 'ai',
    name: 'AI',
    component: AI,
  },
  {
    path: 'economyidx',
    name: 'EconomyStats',
    component: EconomyStats,
  },
  {
    path: 'stockchart',
    name: 'StockChart',
    component: StockChart,
  },
  {
    path:'qtrtrend',
    name:'qtrTrend',
    component:QtrStockTrend
  },
  {
    path:'',
    name:'/dashboard',
    component:()=> import('@/views/MainLayout.vue')
  }
    ]
  },
  {
    path: '/register',
    name: 'RegisterUser',
    component: RegisterUser,
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
  const isAuthenticated = await verifyToken(token);
  if (to.name !== 'Auth' && to.name !== 'RegisterUser'&&!isAuthenticated){ 
    return {name:'Auth'}

    }
    console.log('router allowed!')
    return true;
});


export default router;