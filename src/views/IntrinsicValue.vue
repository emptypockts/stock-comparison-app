<template>
  <div v-if="tickers.length > 0">
    <div class="terminal">
      <span>eacsa> </span>new intrinsic value:
      <button :disabled="loading.isLoading" @click="calculateIntrinsicValue" class="buttons">
        {{ loading['isLoading'] ? 'generating report' : 'GO' }}
      </button>

    </div>
    <div v-for="(ticker, index) in tickers" :key="index" class="table-container">
      <div class="input-row">
        <div style="border: blue 1px solid; gap: 2px 4px;padding: 8px; margin-top: 10px;">
          <label for=" growthRate">Growth Rate (%) default 5%</label>
          <input v-model.number="intrinsicParams[ticker].growthRate" id="growthRate" class="terminal-input" />
          <span v-if="!intrinsicParams[ticker].growthRate">Empty</span>
        </div>
        <div style="border: blue 1px solid; gap: 2px 4px;padding: 8px;margin-top: 10px;">
          <label for=" discountRate">Discount Rate (%) WACC default 10%</label>
          <input v-model.number="intrinsicParams[ticker].discountRate" id="discountRate" class="terminal-input" />
          <span v-if="!intrinsicParams[ticker].discountRate">Empty</span>
        </div>
        <div style="border: blue 1px solid; gap: 2px 4px;padding: 8px;margin-top: 10px;">
          <label for=" terminalGrowthRate">Terminal Growth Rate (%) default 2%</label>
          <input v-model.number="intrinsicParams[ticker].terminalGrowthRate" id="terminalGrowthRate"
            class="terminal-input" />
          <span v-if="!intrinsicParams[ticker].terminalGrowthRate">Empty</span>
        </div>
        <div style="border: blue 1px solid; gap: 2px 4px;padding: 8px;margin-top: 10px;">
          <label for=" projectionYears">Projection Years default 5y</label>
          <input v-model.number="intrinsicParams[ticker].projectionYears" id="projectionYears" class="terminal-input" />
          <span v-if="!intrinsicParams[ticker].projectionYears">Empty</span>
        </div>
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

      </div>
      <div>
        <table>
          <thead>
            <tr>
              <th>Ticker</th>
              <th>Company Name</th>
              <th>Current Price</th>
              <th>Estimated earnings growth +1y</th>

              <!-- Intrinsic Value Models (collapsible) -->
              <th v-if="!collapsed">Intrinsic Value (DCF)</th>
              <th v-if="!collapsed">Graham Value</th>
              <th v-if="!collapsed">DDM Value</th>
              <th v-if="!collapsed">RIM Value</th>
              <th v-if="!collapsed">APV Value</th>
              <th v-if="!collapsed">EPV Value</th>
              <th v-if="!collapsed">Asset-Based Value</th>

              <!-- Safety Margins -->
              <th>Below 30% Margin (DCF)</th>
              <th>Below 30% Margin (Graham)</th>
              <th>Below 30% Margin (DDM)</th>
              <th>Below 30% Margin (RIM)</th>
              <th>Below 30% Margin (APV)</th>
              <th>Below 30% Margin (EPV)</th>
              <th>Below 30% Margin (Asset-Based)</th>

              <!-- Safety Margin Prices -->
              <th v-if="!collapsed">Price -30% DCF</th>
              <th v-if="!collapsed">Price -30% Graham</th>
              <th v-if="!collapsed">Price -30% DDM</th>
              <th v-if="!collapsed">Price -30% RIM</th>
              <th v-if="!collapsed">Price -30% APV</th>
              <th v-if="!collapsed">Price -30% EPV</th>
              <th v-if="!collapsed">Price -30% Asset-Based</th>
            </tr>
          </thead>

          <tbody>
            <tr v-for="(item, index) in intrinsicData" :key="index">

              <!-- Identity -->
              <td>{{ item['Ticker'] }}</td>
              <td>{{ item['Company Name'] }}</td>
              <td>{{ item['Current Price'] }}</td>

              <!-- Growth -->
              <td>{{ item['Estimaded earnings +1y %'] }}%</td>

              <!-- Intrinsic Values -->
              <td v-if="!collapsed">{{ item['Intrinsic Value (DCF)'] }}</td>
              <td v-if="!collapsed">{{ item['Graham Value'] }}</td>
              <td v-if="!collapsed">{{ item['DDM Value'] }}</td>
              <td v-if="!collapsed">{{ item['RIM Value'] }}</td>
              <td v-if="!collapsed">{{ item['APV Value'] }}</td>
              <td v-if="!collapsed">{{ item['EPV Value'] }}</td>
              <td v-if="!collapsed">{{ item['Asset-Based Value'] }}</td>

              <!-- Safety Margin Checks -->
              <td :style="safetyStyle(item['Below 30% Safety Margin (DCF)'])"
                :title="tooltipText(item['Below 30% Safety Margin (DCF)'], 'DCF')">
                {{ safetyIcon(item['Below 30% Safety Margin (DCF)']) }}
              </td>

              <td :style="safetyStyle(item['Below 30% Safety Margin (Graham)'])"
                :title="tooltipText(item['Below 30% Safety Margin (Graham)'], 'Graham')">
                {{ safetyIcon(item['Below 30% Safety Margin (Graham)']) }}
              </td>

              <td :style="safetyStyle(item['Below 30% Safety Margin (DDM)'])"
                :title="tooltipText(item['Below 30% Safety Margin (DDM)'], 'DDM')">
                {{ safetyIcon(item['Below 30% Safety Margin (DDM)']) }}
              </td>

              <td :style="safetyStyle(item['Below 30% Safety Margin (RIM)'])"
                :title="tooltipText(item['Below 30% Safety Margin (RIM)'], 'RIM')">
                {{ safetyIcon(item['Below 30% Safety Margin (RIM)']) }}
              </td>

              <td :style="safetyStyle(item['Below 30% Safety Margin (APV)'])"
                :title="tooltipText(item['Below 30% Safety Margin (APV)'], 'APV')">
                {{ safetyIcon(item['Below 30% Safety Margin (APV)']) }}
              </td>

              <td :style="safetyStyle(item['Below 30% Safety Margin (EPV)'])"
                :title="tooltipText(item['Below 30% Safety Margin (EPV)'], 'EPV')">
                {{ safetyIcon(item['Below 30% Safety Margin (EPV)']) }}
              </td>

              <td :style="safetyStyle(item['Below 30% Safety Margin (Asset-Based)'])"
                :title="tooltipText(item['Below 30% Safety Margin (Asset-Based)'], 'Asset-Based')">
                {{ safetyIcon(item['Below 30% Safety Margin (Asset-Based)']) }}
              </td>



              <!-- Price needed with margin -->
              <td v-if="!collapsed">{{ item['Price - 30% Safety Margin (DCF)'] }}</td>
              <td v-if="!collapsed">{{ item['Price - 30% Safety Margin (Graham)'] }}</td>
              <td v-if="!collapsed">{{ item['Price - 30% Safety Margin (DDM)'] }}</td>
              <td v-if="!collapsed">{{ item['Price - 30% Safety Margin (RIM)'] }}</td>
              <td v-if="!collapsed">{{ item['Price - 30% Safety Margin (APV)'] }}</td>
              <td v-if="!collapsed">{{ item['Price - 30% Safety Margin (EPV)'] }}</td>
              <td v-if="!collapsed">{{ item['Price - 30% Safety Margin (Asset-Based)'] }}</td>

            </tr>
          </tbody>
        </table>
      </div>
    </div>
        <div>
      <legend style="font-weight: bold; font-size: 1rem; padding: 0 6px;">
    📌 How to Interpret Valuation Models
  </legend>
      <button @click="toggleCollapse" class="buttons">
        ⟬⟬ expand/collapse ⟭⟭
      </button>
      
      <div v-if="!collapsed">

        <fieldset style="margin-bottom: 14px; padding: 12px; border: 1px solid #666; border-radius: 6px;">

  <small style="line-height: 1.4; display: block; color: #ddd; font-size: 0.85rem;">
    Not all valuation models apply equally to every business. Use the method(s) most aligned with the company’s
    business model, financial structure, and maturity stage.
    <br><br>

    <strong>DCF (Discounted Cash Flow):</strong> Best when the company generates stable, predictable positive free cash flow. if fcf is negative, it will scale down the calculation significantly 📉  
    <br>

    <strong>Graham Value:</strong> Useful for traditional value or asset-heavy businesses where earnings and book value matter.  
    <br>

    <strong>DDM (Dividend Discount Model):</strong> Only relevant if the company consistently pays and grows dividends.  
    <br>

    <strong>RIM (Residual Income Model):</strong> Best for banks, financials, or firms where earnings reflect value more than free cash flow.  
    <br>

    <strong>APV (Adjusted Present Value):</strong> Useful if the firm's leverage is changing or debt strategy impacts valuation.  
    <br>

    <strong>EPV (Earnings Power Value):</strong> Appropriate for cyclical or stable firms when growth is uncertain — assumes no growth.  
    <br>

    <strong>Asset-Based Value:</strong> Applies to distressed companies, holding companies, or asset-heavy operators. Serves as a valuation floor.

    <br><br>
    <em>Tip: A stock becomes compelling when multiple relevant models agree that price is below intrinsic value.</em>
  </small>
</fieldset>

</div>
</div>
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
        const safetyStyle = (value) => {
      if (value === null || value === undefined) return { color: '#aaa' };

      return {
        color: value ? 'limegreen' : 'crimson',
        fontWeight: 'bold'
      };
    };

    const safetyIcon = (value) => {
      if (value === null || value === undefined) return "⚪";
      return value ? "🟢" : "🔴";
    };

    const valuationStyle = (current, intrinsic) => {
      if (!intrinsic || !current) return {};

      let numericIntrinsic = Number(String(intrinsic).replace(/[$,]/g, ""));
      let numericCurrent = Number(String(current).replace(/[$,]/g, ""));

      return {
        color: numericCurrent < numericIntrinsic ? 'limegreen' : 'crimson',
        fontWeight: '600'
      };
    };
    const tooltipText = (value, methodName) => {
      if (value === null || value === undefined)
        return `${methodName}: No valuation data available`;

      return value
        ? `${methodName}: ✔ Stock is BELOW the 30% safety margin.\nThis suggests the price may be undervalued.`
        : `${methodName}: ✖ Stock is ABOVE the 30% safety margin.\nThis suggests it may be overvalued or fairly priced.`;
    };
    return {
      intrinsicData,
      collapsed,
      loading,
      intrinsicParams,
      errorMessage, // Return errorMessage for template
      toggleCollapse,
      calculateIntrinsicValue,
      safetyIcon,
      safetyStyle,
      tooltipText,
    };
  },
  
};
</script>
<style scoped></style>
