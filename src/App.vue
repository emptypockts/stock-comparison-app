
<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <div class="page">
    <div v-if="!isAuthenticated">
      <router-view></router-view>
      
    </div>
    
    <div v-else :class="containerClass" >
  <!-- Floating Logout Button -->
  <svg 
  @click="logout" 
  class="logout-container"
  style="margin: 2rem; height:2em" 
  xmlns="http://www.w3.org/2000/svg" 
  viewBox="0 0 512 512"
  fill="currentColor"
  >
  <path d="M377.9 105.9L500.7 228.7c7.2 7.2 11.3 17.1 11.3 27.3s-4.1 20.1-11.3 27.3L377.9 406.1c-6.4 6.4-15 9.9-24 9.9c-18.7 0-33.9-15.2-33.9-33.9l0-62.1-128 0c-17.7 0-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32l128 0 0-62.1c0-18.7 15.2-33.9 33.9-33.9c9 0 17.6 3.6 24 9.9zM160 96L96 96c-17.7 0-32 14.3-32 32l0 256c0 17.7 14.3 32 32 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32l-64 0c-53 0-96-43-96-96L0 128C0 75 43 32 96 32l64 0c17.7 0 32 14.3 32 32s-14.3 32-32 32z"/>
  
</svg>
      <div id="app">
        <LoginAlert v-if="showLoginAlert"/>
        <!-- Main content on the left side -->
        <div >
          <CompanyNames @tickers-updated="updateTickers" />
        </div>
        <!-- Value Analysis -->
        <div>
          <ValueStockAnalysis :tickers="tickers" :loading="loading" />
        </div>
        <!-- Stock Financial Charts on the right side -->
        <div class="right-content">
          <StockFinancialCharts :tickers="tickers" />
        </div>
        <!-- Intrinsic Value section -->
        <div>
          <IntrinsicValue :tickers="tickers" />
        </div>
        <!-- Rittenhouse Analysis -->
        <!-- <div>
          <RittenhouseAnalysis :tickers="tickers" />
        </div> -->
      </div>
      
    </div>
  </div>
  <SpeedInsights />
  
</template>

<script>

import LoginAlert from "./components/LoginAlert.vue";
import { SpeedInsights } from "@vercel/speed-insights/vue"
import { ref, computed,onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import IntrinsicValue from './components/IntrinsicValue.vue';
import CompanyNames from './components/CompanyNames.vue';
import RittenhouseAnalysis from './components/RittenhouseAnalysis.vue';
import StockFinancialCharts from './components/StockFinancialCharts.vue';
import ValueStockAnalysis from './components/ValueStockAnalysis.vue';
import axios from 'axios'; // Import Axios for HTTP requests

export default {
  name: 'App',
  components: {
    CompanyNames,
    StockFinancialCharts,
    ValueStockAnalysis,
    RittenhouseAnalysis,
    IntrinsicValue,
    LoginAlert,
  },
  setup() {
    const showLoginAlert = ref(true);
    const tickers = ref([]);
    const loading = ref(false);
    const isAuthenticated=ref(false);
    const router = useRouter();
    const route = useRoute(); // Get access to the current route
    const updateTickers = (newTickers) => {
      tickers.value = newTickers;
      loading.value = false; // Data is ready, stop loading

    };
    const setLoading = (status) => {
      loading.value = status; // Set loading status based on the passed value
    };
    
    const verifyToken = async () => {
  const token = localStorage.getItem('token');
  if (!token) return false;
  try {
    const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/verify`, null, {
      headers: {
        'token': token,
      },
    });
    if (response.data.success) {
      console.log('Token is valid');
      return true;
    } else {
      console.log('Token verification failed:', response.data.message);
      return false;
    }
  } catch (error) {
    console.log('Error verifying token:', error);
    return false;
  }
};
onMounted(() => {
  verifyToken().then(result => {
    isAuthenticated.value = result; // Reactive update when token is verified
  });
});
    
const containerClass = computed(() => {
      return tickers.value.length > 0 ? 'app-container-full' : 'app-container';
    });

    const logout = () => {
      // Clear token from localStorage
      localStorage.removeItem('token');
      localStorage.removeItem('tokenExpiration')
      // Redirect to login page
      router.replace('/');
      console.log("Logout successful, routing to the login app");
    };



    return {
      tickers,
      loading,
      isAuthenticated,
      logout,
      updateTickers,
      setLoading,
      showLoginAlert,
      containerClass,
    };
  },
};
</script>

<style scoped>

.page{
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
  background: repeat center url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=2225&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
}

.app-container {
  margin-left: 20px;
  width: 100vw;
  background:transparent;
  height: 98vh;
}

.app-container-full {
  margin-left: 20px;
  width: 100vw;
  background:transparent;
  height: 98%;
}

tr{
  background:transparent;
}

.logout-container{
  position: fixed;
  bottom: 20px;   /* Distance from the bottom of the screen */
  right: 20px;    /* Distance from the right of the screen */
  cursor: pointer;
  color: #6e6e6e8f; /* Customize the icon color */
  z-index: 1000;  /* Ensure it's on top of other elements */
  transition: color 0.3s ease;
}

.logout-container:hover{
  color: #3e3e3ece; /* Customize the icon color */
}

h1 {
  font-size: auto;
  margin-bottom: 20px;
  color: #333;
  text-align: left;
  font-weight: bold;
}

button {
  background-color: #8bb4e0;
}

button:hover{
  background-color: #468eda;
}
</style>
