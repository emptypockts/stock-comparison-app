
<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <div >
    <div v-if="!isAuthenticated">
      <router-view></router-view>

    </div>
    <div v-else class="app-container" >
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
      <tr>Honcho is a demonstration application and is intended for educational and informational purposes only. The
        content and data provided within the application do not constitute financial advice, investment recommendations,
        or professional guidance. Users should not rely on Honcho for making financial decisions.
        I, as the creator of Honcho, am not responsible or liable for any losses, damages, or negative consequences that
        may arise from the use of this application. Always seek professional financial advice before making any
        investment or financial decisions. 
          </tr>
         <tr>p/b ratio is calculated using the Stockholders Equity instead of the tangible book value.</tr>
         <tr>feedback is welcome at cloudmagicstreet@outlook.com</tr>
      <div id="app">
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

import { SpeedInsights } from "@vercel/speed-insights/vue"
import { ref, computed } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import IntrinsicValue from './components/IntrinsicValue.vue';
import CompanyNames from './components/CompanyNames.vue';
import RittenhouseAnalysis from './components/RittenhouseAnalysis.vue';
import StockFinancialCharts from './components/StockFinancialCharts.vue';
import ValueStockAnalysis from './components/ValueStockAnalysis.vue';


export default {
  name: 'App',
  components: {
    CompanyNames,
    StockFinancialCharts,
    ValueStockAnalysis,
    RittenhouseAnalysis,
    IntrinsicValue,
  },
  setup() {
    const tickers = ref([]);
    const loading = ref(false);
    const router = useRouter();
    const route = useRoute(); // Get access to the current route
    const updateTickers = (newTickers) => {
      tickers.value = newTickers;
      loading.value = false; // Data is ready, stop loading
    };
    const setLoading = (status) => {
      loading.value = status; // Set loading status based on the passed value
    };
    const token = localStorage.getItem('token');
    
    const verifyToken = async () => {
      if (!token) return false;
      try {
        const response = await axios.post('/api/verify', {}, {
          headers: {
            'token': token,
          },
        });
        // Check if the token is still valid
        if (response.data.success) {
          console.log('Token is valid');
          return true;
        } else {
          console.log('Token verification failed:', response.data.message);
          return false;
        }
      } catch (error) {
        console.log('Error verifying token:', response.data.message);
        return false;
      }
    };

    const isAuthenticated = computed(() => !!localStorage.getItem('token'));

    const currentRouteName = computed(() => route.name); // Get current route name

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
      currentRouteName, // Expose the current route name
      updateTickers,
      setLoading,
      
    };
  },
};
</script>

<style scoped>


.app-container {
  position: relative;
  width: 100vw;
  background: repeat-y center url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=2225&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
  min-height: 100vh;
  z-index: 0;
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
  color: rgb(175, 175, 175);
}
</style>
