<template>
  <div>
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
      <h1>Honcho for Honchos</h1>
      <div id="app">
        <!-- Main content on the left side -->
        <div class="main-layout">
          <CompanyNames @tickers-updated="updateTickers" />
        </div>
        <!-- Value Analysis -->
        <div>
          <ValueStockAnalysis :tickers="tickers" :loading="loading"/>
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
.reg-container button{
  width: auto;
  position: absolute;
  top: 20px;
  right: 20px;
  display: block;
  width: auto;
  justify-content: center;
  padding: 10px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin: 0 auto;
}
.reg-container button:hover {
  background-color: #8bb4e0;
}

.logout-container button{
  width: auto;
  position: absolute;
  top: 20px;
  right: 20px;
  display: block;
  width: auto;
  justify-content: center;
  padding: 10px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin: 0 auto;
}
.logout-container button:hover {
  background-color: #8bb4e0;
}
h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #333;
  text-align: left;
  font-weight: bold;
}
</style>
