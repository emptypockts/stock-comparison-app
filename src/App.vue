<template>
  <meta name="viewport" content="width=device-width, initial-scale=0.5">
  <div id="app">
      <div v-if="isLoading" class="loading-overlay">
    <div class="loading-throbber">
      <div class="spinner">
      </div>
    </div>
    </div>
    <!-- Navigation visible on all pages -->
    <!-- Main Area -->
      <div v-if="isAuthenticated">
        <Navigation/>
        <div>
          <CookieBanner />
          <LoginAlert />
        </div>
        <div>
          <h1 class="app-title">Welcome to Honcho</h1>
          <CompanyData @tickers-updated="updateTickers" />
        </div>
        <div>
          <ValueStockAnalysis :tickers="tickers"/>
        </div>
        <div>
          <StockFinancialCharts :tickers="tickers" />
        </div>
        <div>
          <IntrinsicValue :tickers="tickers"  />
        </div>
        <div>
          <RittenhouseAnalysis Analyis :tickers="tickers"  />
        </div>
      </div>
      <div v-else>
        <router-view />
      </div>
    </div>
</template>

<script>
import CookieBanner from "./components/CookieBanner.vue";
import LoginAlert from "./components/LoginAlert.vue";
import { ref, computed, onMounted } from 'vue';
import IntrinsicValue from './views/IntrinsicValue.vue';
import CompanyData from './views/CompanyData.vue';
import StockFinancialCharts from './views/StockFinancialCharts.vue';
import ValueStockAnalysis from './views/ValueStockAnalysis.vue';
import axios from 'axios'; // Import Axios for HTTP requests
import { useRouter } from 'vue-router';
import StockChart from "./views/StockChart.vue";
import Navigation from "./components/Navigation.vue";
import RittenhouseAnalysis from "./views/RittenhouseAnalysis.vue";
import { useLoadingStore } from "./stores/loadingStore";



export default {
  name: 'App',
  components: {
    CompanyData,
    StockFinancialCharts,
    ValueStockAnalysis,
    IntrinsicValue,
    LoginAlert,
    CookieBanner,
    StockChart,
    Navigation,
    RittenhouseAnalysis
  },

  setup() {
    const loadingStore = useLoadingStore();
    const showLoginAlert = ref();
    const tickers = ref([]);
    const isAuthenticated = ref(false);
    const router = useRouter();
    const updateTickers = (newTickers) => {
      tickers.value = newTickers;
      localStorage.setItem('ticker', newTickers[0]);

    };

    const clearLocalStorage = () => {
      localStorage.clear()
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
          localStorage.setItem('isAuthenticated','true')
          return true;
        } else {
          console.log('Token verification failed:', response.data.message);
          clearLocalStorage();
          router.push('/Auth');
          return false;
        }
      } catch (error) {
        console.log('Error verifying token ', error)
        clearLocalStorage();
        router.push('/');
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

    const verifyLoginAlert = computed(() => {
      showLoginAlert.value = localStorage.getItem('loginAlert')
      console.log("Login Alert", showLoginAlert.value)
      return showLoginAlert
    });
    
    const isLoading=computed(()=>loadingStore.isLoading)

    return {
      tickers,
      isAuthenticated,
      updateTickers,
      showLoginAlert,
      containerClass,
      verifyLoginAlert,
      isLoading
    };
  },
};
</script>

<style scoped>


tr {
  background: transparent;
}

.navigation {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: rgba(76, 114, 237, 0);
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
  backdrop-filter: blur(10px);
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
.disabled-content{
  pointer-events: none;
  opacity: .5;
  filter: blur(5px);
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
