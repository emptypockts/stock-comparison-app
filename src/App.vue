<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <div class="app-container">
    <div v-if="!isAuthenticated">
      <router-view></router-view>
      <!-- Conditionally show the Register button only on the login page -->
      <div v-if="currentRouteName === 'Auth'" class="reg-container">
        <button @click="goToRegister">Create Account</button>
      </div>
    </div>
    <div v-else>
      <div class="logout-container">
        <button @click="logout">Logout</button>
      </div>
      <tr>Honcho is a demonstration application and is intended for educational and informational purposes only. The
        content and data provided within the application do not constitute financial advice, investment recommendations,
        or professional guidance. Users should not rely on Honcho for making financial decisions.
        I, as the creator of Honcho, am not responsible or liable for any losses, damages, or negative consequences that
        may arise from the use of this application. Always seek professional financial advice before making any
        investment or financial decisions.
        p/b ratio is calculated using the Stockholders Equity instead of the tangible book value.  </tr>
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
</template>

<script>
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
    const isAuthenticated = computed(() => !!localStorage.getItem('token'));

    const currentRouteName = computed(() => route.name); // Get current route name

    const logout = () => {
      // Clear token from localStorage
      localStorage.removeItem('token');
      // Redirect to login page
      router.push('/');
      console.log("Logout successful, routing to the login app");
    };

    const goToRegister = () => {
      // Redirect to the registration page
      console.log("button pushed")
      router.push('/register');
    };

    return {
      tickers,
      loading,
      isAuthenticated,
      logout,
      goToRegister,
      currentRouteName, // Expose the current route name
      updateTickers,
      setLoading,
    };
  },
};
</script>

<style scoped>
html,
body {
  margin: 0;
  padding: 0;
  overflow: hidden;
  /* Prevents scrollbars from appearing */
}

.app-container {
  position: relative;
  width: 100vw;
  background: repeat-y center url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=2225&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
  min-height: 100vh;
  z-index: 0;
}

.reg-container button {
  width: auto;
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: block;
  width: auto;
  justify-content: center;
  padding: 10px;
  color: rgb(136, 136, 136);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin: 0 auto;
}

.reg-container button:hover {
  background-color: #8bb4e0;
}

.logout-container button {
  width: auto;
  position: absolute;
  bottom: 20px;
  right: 20px;
  display: block;
  width: auto;
  justify-content: center;
  padding: 10px;
  color: rgb(136, 136, 136);
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin: 0 auto;
  z-index: 1;
}

.logout-container button:hover {
  background-color: #8bb4e0;
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
