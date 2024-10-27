<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <div class="page">
    <div v-if="!isAuthenticated">
      <h1 class="app-title">Welcome to Honcho</h1> <!-- Add your title here -->
      <router-view></router-view>
    </div>
    <div v-else :class="containerClass">
      <Logout />
      <BotLogo />
      <economyIdxLogo />
      <GoBack />
      <div id="app">
        <CookieBanner />
        <LoginAlert v-if="showLoginAlert" />
        <!-- Main content on the left side -->
        <div>
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
</template>

<script>
import CookieBanner from "./components/CookieBanner.vue";
import LoginAlert from "./components/LoginAlert.vue";
import { ref, computed, onMounted } from 'vue';
// import { useRouter, useRoute } from 'vue-router';
import IntrinsicValue from './components/IntrinsicValue.vue';
import CompanyNames from './components/CompanyNames.vue';
// import RittenhouseAnalysis from './components/RittenhouseAnalysis.vue';
import StockFinancialCharts from './components/StockFinancialCharts.vue';
import ValueStockAnalysis from './components/ValueStockAnalysis.vue';
import axios from 'axios'; // Import Axios for HTTP requests
import Logout from "./components/Log_out.vue";
import BotLogo from "./components/botLogo.vue";
import economyIdxLogo from "./components/economyIdxLogo.vue";
import GoBack from "./components/goBack.vue";



export default {
  name: 'App',
  components: {
    CompanyNames,
    StockFinancialCharts,
    ValueStockAnalysis,
    // RittenhouseAnalysis,
    IntrinsicValue,
    LoginAlert,
    CookieBanner,
    Logout,
    BotLogo,
    economyIdxLogo,
    GoBack,
  },
  setup() {
    const showLoginAlert = ref(true);
    const tickers = ref([]);
    const loading = ref(false);
    const isAuthenticated = ref(false);
    // const router = useRouter();
    // const route = useRoute(); // Get access to the current route
    const updateTickers = (newTickers) => {
      tickers.value = newTickers;
      localStorage.setItem('ticker', newTickers[0])
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
          localStorage.removeItem('token');
          localStorage.removeItem('tokenExpiration')
          localStorage.removeItem('cookieAccepted')
          localStorage.removeItem('cookieAcceptedTimestamp')
          localStorage.removeItem('cookieDeclined')
          localStorage.removeItem('ticker')
          console.log("Logout successful, routing to the login app");
          // Redirect to login page
          router.replace('/');
          return false;
        }
      } catch (error) {
        console.log('Error verifying token:', error);
        localStorage.removeItem('token');
        localStorage.removeItem('tokenExpiration')
        localStorage.removeItem('cookieAccepted')
        localStorage.removeItem('cookieAcceptedTimestamp')
        localStorage.removeItem('cookieDeclined')
        localStorage.removeItem('ticker')
        console.log("Logout successful, routing to the login app");
        // Redirect to login page
        router.replace('/');
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




    return {
      tickers,
      loading,
      isAuthenticated,
      updateTickers,
      setLoading,
      showLoginAlert,
      containerClass,
    };
  },
};
</script>

<style scoped>
.page {
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background: repeat center url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=2225&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
  flex-direction: column-reverse;
}

.app-container {
  margin-left: 20px;
  width: 98vw;
  background: transparent;
  height: 98vh;
}

.app-container-full {
  margin-left: 20px;
  width: 100vw;
  background: transparent;
  height: 98%;
}

tr {
  background: transparent;
}



button {
  background-color: #8bb4e0;
}

button:hover {
  background-color: #468eda;
}
</style>

<style>
* {
  font-family: monospace;
}

h1,
h2 {

  font-size: auto;
  margin-bottom: 20px;
  margin-left: 10px;
  color: #6d6d6d;
  text-align: left;
  font-weight: bold;

}

/* Loading overlay styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-throbber {
  text-align: center;
  color: white;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  width: 50px;
  height: 50px;
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.app-title {
  font-size: 2em;
  text-align: center;
  color: #6d6d6d;
  margin-bottom: 20px;
  font-weight: bold;
  width: 100%;
  /* Ensure it takes the full width */
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>
