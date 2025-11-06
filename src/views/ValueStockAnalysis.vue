<template>
  <div>
    <h1 class="app-title">Value Stock Analysis</h1>
    <!-- Error message display -->
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>
  </div>
  <button :disabled="tickers.length === 0" @click="toggleCollapse">
    Click to expand or collapse
  </button>
    <div v-if="financialData.length" class="table-container" >
      <small>
        ⚠️The score printed is not an individual analysis but an average of the 5 years or the number of years available for this stock
      </small>
      <div class="table-scroll">
        <table class="copyable-table">
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
    <!-- <div v-else>
        <p>No financial data available. Please try fetching data for different tickers.</p>
      </div> -->
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
.table-container {
  overflow-x: auto;
  /* Enable horizontal scrolling if the table is too wide */
}

table {
  width: 100%;
  border-collapse: collapse;
}

thead th,
tbody td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
  user-select: text;
  /* Ensure text can be selected */
}


tbody tr:hover {
  background-color: #f9f9f9;
  /* Optional: highlight row on hover */
}

/* Add CSS class to allow easy selection and copying */
.copyable-table {
  user-select: text;
  /* Ensure that table text can be selected for copying */
}

.title-container {
  justify-content: auto;
  /* Adjusts space between the title and the button */
  align-items: center;
  /* Vertically aligns the button and title */
}

.title-container h1 {
  margin-right: 10px;
  /* Optional: adds some space between the title and button */
}

.title-container button {
  margin-left: 10px;
  /* Optional: adds some space between the button and title */
  margin-top: 5px;
}

@media screen and (max-width: 768px) {

  th,
  td {
    padding: 0px;
  }
}

/* Same loading screen styles */
.loading-screen {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  color: white;
  font-size: 1.5em;
  z-index: 1000;
}

</style>
