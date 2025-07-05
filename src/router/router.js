import { createRouter, createWebHistory } from 'vue-router';
import AuthPage from '@/views/AuthPage.vue';
import RegisterUser from '@/views/RegisterUser.vue';
import AI from '@/views/AI.vue';
import EconomyStats from '@/views/EconomyStats.vue';
import StockChart from '@/views/StockChart.vue';
import QtrStockTrend from '@/views/QtrStockTrend.vue';
import { verifyCfToken } from '@/utils/auth';
import App from '@/layouts/App.vue';
import { useTickerStore } from '@/stores/tickerStore';
import MainLayout from '@/views/MainLayout.vue';

const router = createRouter({
  history:createWebHistory(),
  routes:[
  {
    path: '/login',
    name: 'Auth',
    component: AuthPage,
  },
  {
    path: '/',
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
    name:'Home',
    component: MainLayout
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
  const tickerStore=useTickerStore()
  const isAuthenticated = await verifyCfToken();
  if (to.name !== 'Auth' && to.name !== 'RegisterUser'&&!isAuthenticated){ 
    return {path:'/'}

    }
  if (to.name==='Auth' && isAuthenticated){
    return {path:'/'}
  }
    

    tickerStore.deleteTickers();
    return true;

});


export default router;