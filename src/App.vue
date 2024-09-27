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
      <button class="logout-container" @click="logout">Logout</button>
      <h1>Honcho me</h1>
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
/* Position the logout button in the top-right corner */
.logout-container {
  position: absolute;
  top: 20px;
  right: 20px;
}

.logout-container button {
  width: 100%;
  padding: 10px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.logout-container button:hover {
  background-color: #ff0000;
}

/* Style for the Register button */
.reg-container {
  position:absolute;
  top: 10px;
  right: 10px;
  text-align: right;
}

.reg-container button {
  display: block;
  width: auto;
  justify-content: center;
  padding: 10px;
  background-color: #29ac94;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 auto;
}

.auth-container button:hover {
  background-color: #0056b3;
}

/* Main layout styling */
.main-layout {
  display: flex;
  justify-content: space-between;
  gap: 20px;
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.left-content {
  flex: 2;
}

.right-content {
  flex: 1;
}

/* Full-width content (Rittenhouse Analysis) */
.full-width-content {
  padding: 20px;
  background-color: #f8f9fa;
  margin-top: 20px;
}

/* General styling */
#app {
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
  color: #333;
  background-color: #ffffff;
  line-height: 1.6;
}

h1, h2, h3, h4, h5, h6 {
  color: #007bff;
  margin-bottom: 20px;
}

p {
  color: #666;
}

a {
  color: #007bff;
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}
</style>
