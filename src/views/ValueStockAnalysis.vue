<template>
  <div v-if="tickers.length>0">
  <div>
    <!-- Error message display -->
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>
    <div class="terminal">
      <span >eacsa> </span>value stock index 0-7:
    </div>
  </div>
      <div v-if="!collapsed">
        <p>
          revenue strength, financial health, and value signals. real investors do not yolo, we verify.
        </p>
      </div>
      <div>
          <button @click="toggleCollapse" class="buttons">
        ⟬⟬ expand/collapse ⟭⟭
      </button>
      </div>
      
    <div v-if="financialData.length" class="table-container">
        <table >
          <thead>
            <tr>
              <th>Date</th>
              <th>Total Score</th>
                <th v-if="!collapsed">Basic Average Shares</th>
                <th v-if="!collapsed">Basic EPS</th>
                <th v-if="!collapsed">Diluted EPS</th>
                <th v-if="!collapsed">Dividends</th>
                <th v-if="!collapsed">Dividends Yield</th>
                <th v-if="!collapsed">Earnings Yield</th>
                <th v-if="!collapsed">Free Cash Flow</th>
                <th v-if="!collapsed">Market Cap</th>
                <th v-if="!collapsed">Price Per Share</th>
                <th v-if="!collapsed">Tangible Book Value</th>
                <th v-if="!collapsed">Tangible Book Value Per Share</th>
                <th v-if="!collapsed">Total Debt</th>
                <th v-if="!collapsed">p/b ratio</th>
                <th v-if="!collapsed">p/e ratio</th>
                <th v-if="!collapsed">Debt FCF ratio</th>
                <th v-if="!collapsed">Sum of Debt/FCF ratio &gt 0 Score</th>
                <th v-if="!collapsed">Market Cap Score &gt 2B</th>
                <th v-if="!collapsed">p/b ratio &lt 2 Score</th>
                <th v-if="!collapsed">p/e ratio &lt 15 Score</th>
                <th v-if="!collapsed">1.3 Earnings Yield Score</th>
                <th v-if="!collapsed">Dividends Yield &gt 0 Score</th>
                <th v-if="!collapsed">Earnings Yield &gt 0 Score</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in financialData" :key="index">
              <td>{{ item['Date'] }}</td>
              <td>{{ item['Total Score'] }}</td>
                <td v-if="!collapsed">{{ item['Basic Average Shares'] }}</td>
                <td v-if="!collapsed">{{ item['Basic EPS'] }}</td>
                <td v-if="!collapsed">{{ item['Diluted EPS'] }}</td>
                <td v-if="!collapsed">{{ item['Dividends'] }}</td>
                <td v-if="!collapsed">{{ item['Dividends Yield'] }}</td>
                <td v-if="!collapsed">{{ item['Earnings Yield'] }}</td>
                <td v-if="!collapsed">{{ item['Free Cash Flow'] }}</td>
                <td v-if="!collapsed">{{ item['Market Cap'] }}</td>
                <td v-if="!collapsed">{{ item['Price Per Share'] }}</td>
                <td v-if="!collapsed">{{ item['Tangible Book Value'] }}</td>
                <td v-if="!collapsed">{{ item['Tangible Book Value Per Share'] }}</td>
                <td v-if="!collapsed">{{ item['Total Debt'] }}</td>
                <td v-if="!collapsed">{{ item['p/b ratio'] }}</td>
                <td v-if="!collapsed">{{ item['p/e ratio'] }}</td>
                <td v-if="!collapsed">{{ item['Debt FCF ratio'] }}</td>
                <td v-if="!collapsed">{{ item['Sum of Debt/FCF ratio Score'] }}</td>
                <td v-if="!collapsed">{{ item['Market Cap Score'] }}</td>
                <td v-if="!collapsed">{{ item['p/b ratio Score'] }}</td>
                <td v-if="!collapsed">{{ item['p/e ratio Score'] }}</td>
                <td v-if="!collapsed">{{ item['130pcnt_Earnings Yield Score'] }}</td>
                <td v-if="!collapsed">{{ item['Dividends Yield Score'] }}</td>
                <td v-if="!collapsed">{{ item['Earnings Yield Score'] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';
import { useLoadingStore } from '@/stores/loadingStore';
import CompanyData from './CompanyData.vue';
export default {
  emits: ['tickers-updated'], // Declare the custom events
  props: {
    tickers: {
      type: Array,
    },
  },
  setup(props, { emit }) {
    const loading = useLoadingStore();
    const financialData = ref([]); // This will hold the data fetched from the backend
    const collapsed = ref(true); // Controls the visibility of extra columns
    const errorMessage = ref(''); // Variable to store error messages
    const firstLogin = ref(true); // Flag to prevent error message on first load
    const toggleCollapse = () => {
      collapsed.value = !collapsed.value;
    };

    const fetch5YearData = async (tickers) => {
      // Check if the tickers array is empty
      if (!tickers || tickers.length === 0) {
        if (!firstLogin.value) {
          errorMessage.value = 'No tickers provided. Please enter valid tickers.';
        }
        return;
      }

      errorMessage.value = '';

      loading.startLoading();
      try {
        const params = new URLSearchParams();
        tickers.forEach((ticker, index) => params.append(`ticker${index + 1}`, ticker));

        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/5y_data`, {
          params,
        });
        
        financialData.value =response.data;
        
      } catch (error) {
        console.error('Error fetching 5-year financial data:', error);
      } finally {
        loading.stopLoading();
      }
    };

    watch(
      () => props.tickers,
      (newTickers) => {
        if (newTickers.length) {
          fetch5YearData(newTickers);
        }
      },
      { immediate: true }
    );

    onMounted(() => {
      fetch5YearData(props.tickers);
      firstLogin.value = false; // Mark as no longer the first login after mounted
    });

    return {
      financialData,
      collapsed,
      toggleCollapse,
      errorMessage,// Return errorMessage for use in the template
      fetch5YearData,
    };
  },
};
</script>

<style>

</style>
