import { createApp } from 'vue';
import { createPinia } from 'pinia';
import App from './layouts/App.vue';
import router from '@/router/router';

createApp(App)
.use(router)
.use(createPinia())
.mount('#app');





