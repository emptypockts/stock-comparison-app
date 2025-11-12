<template>
  <div v-if="tickers.length > 0">
    <div class="terminal">
        <span>eacsa> </span>new intrinsic value:
                        <button 
                :disabled="loading.isLoading" 
                @click="calculateIntrinsicValue" 
                class="buttons">
            {{loading['isLoading'] ? 'generating report': 'GO'}}
            </button>

      </div>
    <div v-for="(ticker, index) in tickers" :key="index">
      <div class="input-field">
        <label for="growthRate">Growth Rate (%) default 5%</label>
        <input v-model.number="intrinsicParams[ticker].growthRate" id="growthRate" class="terminal-input"
          style="width: 20px;" />
        <span v-if="!intrinsicParams[ticker].growthRate">Empty</span>


        <label for="discountRate">Discount Rate (%) WACC default 10%</label>
        <input v-model.number="intrinsicParams[ticker].discountRate" id="discountRate" class="terminal-input"
          style="width: 20px;" />
        <span v-if="!intrinsicParams[ticker].discountRate">Empty</span>


        <label for="terminalGrowthRate">Terminal Growth Rate (%) default 2%</label>
        <input v-model.number="intrinsicParams[ticker].terminalGrowthRate" id="terminalGrowthRate"
          class="terminal-input" style="width: 20px;" />
        <span v-if="!intrinsicParams[ticker].terminalGrowthRate">Empty</span>


        <label for="projectionYears">Projection Years default 5y</label>
        <input v-model.number="intrinsicParams[ticker].projectionYears" id="projectionYears" class="terminal-input"
          style="width: 20px;" />
        <span v-if="!intrinsicParams[ticker].projectionYears">Empty</span>
      </div>
      


    </div>
    <!-- Error Message Display -->
    <div v-if="errorMessage" class="error-message">
      <p>{{ errorMessage }}</p>
    </div>

    <div v-if="intrinsicData.length" class="table-container">
      <button @click="toggleCollapse" class="buttons">
        ⟬⟬ expand/collapse ⟭⟭
      </button>
      <div v-if="!collapsed">
        dcf engines online. computing what the stock should cost, not what wall street says
      </div>
      <div >
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
    <!-- <div v-else>
      <p>No intrinsic value data available. Please try fetching data for different tickers.</p>
    </div> -->
  </div>
</template>

<script>
import { ref, reactive, onMounted, watch } from 'vue';
import axios from 'axios';
import { useLoadingStore } from '@/stores/loadingStore';
export default {
  props: {
    tickers: {
      type: Array,
    },
  },
  setup(props) {
    const intrinsicData = ref([]);
    const collapsed = ref(true);
    const loading = useLoadingStore();
    const intrinsicParams = reactive({});
    const errorMessage = ref(''); // Variable to store error messages
    const firstLogin = ref(true);
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
        if (!firstLogin.value) {
          errorMessage.value = 'No tickers provided. Please enter valid tickers.';
        }
        return;
      }

      loading.startLoading();
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

      } catch (error) {
        console.error('Error fetching intrinsic value data:', error);
        errorMessage.value = `Failed to fetch intrinsic value data: ${error.response ? error.response.data : error.message}`;
      } finally {
        loading.stopLoading();
      }
    };

    const calculateIntrinsicValue = () => {
      fetchIntrinsicValues(props.tickers);
    };

    onMounted(() => {
      fetchIntrinsicValues(props.tickers);
      firstLogin.value = false; // Mark as no longer the first login after mounted
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
<style scoped></style>
