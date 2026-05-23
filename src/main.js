import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './layouts/App.vue';
import router from '@/router/router';
import '/assets/css/styles/global.css'

// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// import { useSocket } from './composables/taskSocket';

import { WagmiPlugin } from '@wagmi/vue';
import { QueryClient, VueQueryPlugin } from '@tanstack/vue-query'
import { config } from './config';
const queryClient = new QueryClient()
createApp(App)
.use(router)
.use(createPinia())
.use(WagmiPlugin, { config })
.use(VueQueryPlugin, { queryClient })
.mount('#app');

// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// useSocket();