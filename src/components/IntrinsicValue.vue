<template>
  <div class="title-container">
    <h1>Intrinsic Value Analysis</h1>
    <button class="button-calculate" @click="calculateIntrinsicValue">Calculate Intrinsic Value</button>
  </div>
    
    <div>
    <!-- Input fields for each ticker -->
    <div v-for="(ticker, index) in tickers" :key="index" class="input-container">
      <h3>{{ ticker }}</h3>
      <div class="input-group">
        <label for="growthRate">Growth Rate (%) default 5%</label>
        <input v-model.number="intrinsicParams[ticker].growthRate" id="growthRate" type="number" step="0.1" />
        <span v-if="!intrinsicParams[ticker].growthRate">Empty</span>
      </div>
      <div class="input-group">
        <label for="discountRate">Discount Rate (%) WACC default 10%</label>
        <input v-model.number="intrinsicParams[ticker].discountRate" id="discountRate" type="number" step="0.1" />
        <span v-if="!intrinsicParams[ticker].discountRate">Empty</span>
      </div>
      <div class="input-group">
        <label for="terminalGrowthRate">Terminal Growth Rate (%) default 2%</label>
        <input v-model.number="intrinsicParams[ticker].terminalGrowthRate" id="terminalGrowthRate" type="number" step="0.1" />
        <span v-if="!intrinsicParams[ticker].terminalGrowthRate">Empty</span>
      </div>
      <div class="input-group">
        <label for="projectionYears">Projection Years default 5y</label>
        <input v-model.number="intrinsicParams[ticker].projectionYears" id="projectionYears" type="number" step="1" min="1" />
        <span v-if="!intrinsicParams[ticker].projectionYears">Empty</span>
        
      </div>
      
    </div>

    

    <!-- Loading Throbber -->
    <div v-if="loading" class="loading-overlay">
      <div class="loading-throbber">
        <div class="spinner"></div>
        <p>Calculating intrinsic values... Please wait.</p>
      </div>
    </div>

    <!-- Error Message Display -->
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>

    <div v-if="intrinsicData.length" class="table-container">
      <h2>Intrinsic Value Data for {{ tickers.join(', ') }}</h2>
      <button @click="toggleCollapse">Click to expand or collapse</button>
      <div class="table-scroll">
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Current Price</th>
              <th>Below 30% Safety Margin (Graham)</th>
              <th>Below 30% Safety Margin (DCF)</th>
              <th>Estimated earnings growth +1y</th>
              <th v-if="!collapsed">Intrinsic Value (DCF)</th>
              <th v-if="!collapsed">Graham Value</th>
              <th>Price - 30% Safety Margin (Graham)</th>
              <th>Price - 30% Safety Margin (DCF)</th>
              <th v-if="!collapsed">Company Name</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, index) in intrinsicData" :key="index">
              <td>{{ item['Ticker'] }}</td>
              <td>{{ item['Current Price'] }}</td>
              <td>{{ item['Below 30% Safety Margin (Graham)'] }}</td>
              <td>{{ item['Below 30% Safety Margin (DCF)'] }}</td>
              <td>{{ item['Estimaded earnings +1y %'] }}%</td>
              <td v-if="!collapsed">{{ item['Intrinsic Value (DCF)'] }}</td>
              <td v-if="!collapsed">{{ item['Graham Value'] }}</td>
              <td>{{ item['Price - 30% Safety Margin (Graham)'] }}</td>
              <td>{{ item['Price - 30% Safety Margin (DCF)'] }}</td>
              <td v-if="!collapsed">{{ item['Company Name'] }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    <div v-else>
      <p>No intrinsic value data available. Please try fetching data for different tickers.</p>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue';
import axios from 'axios';

export default {
  props: {
    tickers: {
      type: Array,
      required: true,
    },
  },
  setup(props) {
    const intrinsicData = ref([]);
    const collapsed = ref(true);
    const loading = ref(false);
    const intrinsicParams = reactive({});
    const errorMessage = ref(''); // Variable to store error messages

    // Initialize intrinsicParams based on the provided tickers
    const initializeParams = (tickers) => {
      tickers.forEach((ticker) => {
        if (!intrinsicParams[ticker]) {
          intrinsicParams[ticker] = {
            growthRate: 5.0, // Default value for Growth Rate
            discountRate: 10.0, // Default value for Discount Rate
            terminalGrowthRate: 2.0, // Default value for Terminal Growth Rate
            projectionYears: 5, // Default value for Projection Years
          };
        }
      });
    };

    watch(
      () => props.tickers,
      (newTickers) => {
        if (newTickers.length) {
          initializeParams(newTickers);
          fetchIntrinsicValues(newTickers);
        }
      },
      { immediate: true }
    );

    const toggleCollapse = () => {
      collapsed.value = !collapsed.value;
    };

    const fetchIntrinsicValues = async (tickers) => {
      // Check if tickers array is empty
      if (!tickers || tickers.length === 0) {
        errorMessage.value = 'No tickers provided. Please enter valid tickers.';
        return;
      }

      loading.value = true; // Start loading
      errorMessage.value = ''; // Reset error message

      try {
        const params = new URLSearchParams();
        tickers.forEach((ticker, index) => {
          const tickerParams = intrinsicParams[ticker];
          params.append(`ticker${index + 1}`, ticker);
          params.append(`growthRate${index + 1}`, tickerParams.growthRate);
          params.append(`discountRate${index + 1}`, tickerParams.discountRate);
          params.append(`terminalGrowthRate${index + 1}`, tickerParams.terminalGrowthRate);
          params.append(`projectionYears${index + 1}`, tickerParams.projectionYears);
        });

        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/intrinsic_value`, {
          params: params,
        });

        intrinsicData.value = response.data;
        console.log('Intrinsic Value Stock Data: ', response.data);
      } catch (error) {
        console.error('Error fetching intrinsic value data:', error);
        errorMessage.value = `Failed to fetch intrinsic value data: ${error.response ? error.response.data : error.message}`;
      } finally {
        loading.value = false; // End loading
      }
    };

    const calculateIntrinsicValue = () => {
      fetchIntrinsicValues(props.tickers);
    };

    onMounted(() => {
      fetchIntrinsicValues(props.tickers);
    });

    return {
      intrinsicData,
      collapsed,
      loading,
      intrinsicParams,
      errorMessage, // Return errorMessage for template
      toggleCollapse,
      calculateIntrinsicValue,
    };
  },
};
</script>

<style scoped>
/* Same styles with an added error message style */

.input-container {
  display: flex;
  align-items: center;
  gap: 10px;
  /* Add space between inputs and button */
}

input {
  width: auto;
  padding: 8px;
  margin-top: 5px;
  border-radius: 8px;
  border: 1px solid #f1f0f0;
}
.button-calculate {
  display: block;
  width: auto;
  justify-content: auto;
  padding: 8px;
  color: white;
  border: 1px;
  border-radius: 8px;
  cursor: pointer;

}

.button-calculate:hover {
  background-color: #8bb4e0;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5); /* Semi-transparent background to create a shadow effect */
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999; /* High z-index to ensure it overlays all content */
}

.loading-throbber {
  text-align: center;
  color: white;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3); /* Light border for the spinner */
  border-radius: 50%;
  border-top-color: white; /* The top border is solid to create the spinning effect */
  width: 50px;
  height: 50px;
  animation: spin 1s ease-in-out infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Error message style */
.error-message {
  color: red;
  margin-top: 10px;
}

@media screen and (max-width: 768px) {
  th, td {
    padding: 3px;
    font-size: 10px;
  }
}

h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #333;
  text-align: left;
  font-weight: bold;
}

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

.title-container {
  display: flex;
  justify-content: auto; /* Adjusts space between the title and the button */
  align-items: center; /* Vertically aligns the button and title */
}

.title-container h1 {
  margin-right: 10px; /* Optional: adds some space between the title and button */
}

.title-container button {
  margin-left: 10px; /* Optional: adds some space between the button and title */
  margin-top: 5px;
}
</style>
