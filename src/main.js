import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './layouts/App.vue';
import router from '@/router/router';
import '/assets/css/styles/global.css'
import { useSocket } from './composables/taskSocket';

createApp(App)
.use(router)
.use(createPinia())
.mount('#app');
useSocket();