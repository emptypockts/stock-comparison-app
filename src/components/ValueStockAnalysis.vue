<template>
  <div>
    <div v-if="loading" class="loading-screen">
      <p>Loading Value Stock Analysis...</p>
    </div>
    <div v-else>
      <h1>Value Stock Analysis</h1>
            <!-- Error message display -->
            <div v-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
      </div>
      <div v-if="financialData.length" class="table-container">
        <h2>Financial Data for {{ tickers.join(', ') }}</h2>
        <button @click="toggleCollapse">Click to expand or collapse</button>
        <div class="table-scroll">
          <table>
            <thead>
              <tr>
                <th>Date</th>
                <th>Total Score</th>
                <th>Symbol</th>
                <th v-if="!collapsed">Basic Average Shares</th>
                <th v-if="!collapsed">Tangible Book Value</th>
                <th v-if="!collapsed">Free Cash Flow</th>
                <th v-if="!collapsed">Basic EPS</th>
                <th v-if="!collapsed">Diluted EPS</th>
                <th v-if="!collapsed">Total Debt</th>
                <th v-if="!collapsed">Dividends</th>
                <th v-if="!collapsed">Price Per Share</th>
                <th v-if="!collapsed">Tangible Book Value Per Share</th>
                <th v-if="!collapsed">p/b ratio</th>
                <th v-if="!collapsed">p/e ratio</th>
                <th v-if="!collapsed">Debt FCF ratio</th>
                <th v-if="!collapsed">Dividends Yield</th>
                <th v-if="!collapsed">Earnings Yield</th>
                <th v-if="!collapsed">Market Cap</th>
                <th v-if="!collapsed">Market Cap Score</th>
                <th v-if="!collapsed">p/e ratio Score</th>
                <th v-if="!collapsed">p/b ratio Score</th>
                <th v-if="!collapsed">Sum of Debt/FCF ratio Score</th>
                <th v-if="!collapsed">Earnings Yield Score</th>
                <th v-if="!collapsed">1.3 Earnings Yield Score</th>
                <th v-if="!collapsed">Dividends Yield Score</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in financialData" :key="index">
                <td>{{ item['Date'] }}</td>
                <td>{{ item['Total Score'] }}</td>
                <td>{{ item['Symbol'] }}</td>
                <td v-if="!collapsed">{{ item['Basic Average Shares'] }}</td>
                <td v-if="!collapsed">{{ item['Tangible Book Value'] }}</td>
                <td v-if="!collapsed">{{ item['Free Cash Flow'] }}</td>
                <td v-if="!collapsed">{{ item['Basic EPS'] }}</td>
                <td v-if="!collapsed">{{ item['Diluted EPS'] }}</td>
                <td v-if="!collapsed">{{ item['Total Debt'] }}</td>
                <td v-if="!collapsed">{{ item['Dividends'] }}</td>
                <td v-if="!collapsed">{{ item['Price Per Share'] }}</td>
                <td v-if="!collapsed">{{ item['Tangible Book Value Per Share'] }}</td>
                <td v-if="!collapsed">{{ item['p/b ratio'] }}</td>
                <td v-if="!collapsed">{{ item['p/e ratio'] }}</td>
                <td v-if="!collapsed">{{ item['Debt FCF ratio'] }}</td>
                <td v-if="!collapsed">{{ item['Dividends Yield'] }}</td>
                <td v-if="!collapsed">{{ item['Earnings Yield'] }}</td>
                <td v-if="!collapsed">{{ item['Market Cap'] }}</td>
                <td v-if="!collapsed">{{ item['Market Cap Score'] }}</td>
                <td v-if="!collapsed">{{ item['p/e ratio Score'] }}</td>
                <td v-if="!collapsed">{{ item['p/b ratio Score'] }}</td>
                <td v-if="!collapsed">{{ item['Sum of Debt/FCF ratio Score'] }}</td>
                <td v-if="!collapsed">{{ item['Earnings Yield Score'] }}</td>
                <td v-if="!collapsed">{{ item['1.3 Earnings Yield Score'] }}</td>
                <td v-if="!collapsed">{{ item['Dividends Yield Score'] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
      <div v-else>
        <p>No financial data available. Please try fetching data for different tickers.</p>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, watch, onMounted } from 'vue';
import axios from 'axios';

export default {
  emits: ['tickers-updated', 'loading'], // Declare the custom events
  props: {
    tickers: {
      type: Array,
      required: true,
    },
    loading: {
      type: Boolean,
      required: true,
    },
  },
  setup(props, { emit }) {
    const financialData = ref([]); // This will hold the data fetched from the backend
    const collapsed = ref(true); // Controls the visibility of extra columns
    const errorMessage = ref(''); // Variable to store error messages

    const toggleCollapse = () => {
      collapsed.value = !collapsed.value;
    };

    const fetch5YearData = async (tickers) => {
            // Check if the tickers array is empty
            if (!tickers || tickers.length === 0) {
        errorMessage.value = 'No tickers provided. Please enter valid tickers.';
        return;
      }
            // Reset error message and loading state
      errorMessage.value = '';
      // await new Promise(resolve => setTimeout(resolve, 3000)); // 3-second delay
      emit('loading', true); // Emit loading status as true to indicate loading has started

      try {
        const params = new URLSearchParams();
        tickers.forEach((ticker, index) => params.append(`ticker${index + 1}`, ticker));

        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/5y_data`, {
          params,
        });
        financialData.value = response.data;
      } catch (error) {
        console.error('Error fetching 5-year financial data:', error);
      } finally {
        emit('loading', false); // Emit loading status as false to stop loading after the request is complete
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
    });

    return {
      financialData,
      collapsed,
      toggleCollapse,
      errorMessage,// Return errorMessage for use in the template
    };
  },
};
</script>

<style scoped>
.table-container {
  margin-top: 20px;
}

.table-scroll {
  max-width: auto;
  overflow-x: auto; /* Adds a horizontal scrollbar to the table */
}

table {
  width: auto;
  border-collapse: collapse;
}

th, td {
  padding: 4px; /* Reduced padding for more compact columns */
  border: 1px solid #ddd;
  text-align: left;
  font-size: 12px; /* Smaller font size for more compact text */
}

th {
  background-color: #f4f4f4;
  white-space: nowrap; /* Prevent header text from wrapping */
}

td {
  white-space: nowrap; /* Prevent cell text from wrapping */
}

table {
  font-size: 12px;
}

@media screen and (max-width: 768px) {
  th, td {
    padding: 3px;
    font-size: 10px;
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
