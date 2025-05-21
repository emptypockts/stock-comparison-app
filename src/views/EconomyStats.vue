<template>
  <div>
    <div class="title-container">
    <h1>Economic Indicators</h1>
  </div>
    <div>
      <div v-if="indexList.length" class="chart-container">
        <!-- Economic Index Charts -->
        <div v-for="index in indexList" :key="index" class="chart-box">
          <h2>{{ index.name }}</h2>
          <apexcharts v-if="index.series.length" type="line" :options="chartOptions" :series="index.series" />
          <p>{{ index.description }}</p>
        </div>

      </div>
      <div v-else>
        <p class="error-message">{{ errorMessage }}</p>
      </div>
      <div>
        <Navigation/>
      </div>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-throbber">
          <div class="spinner"></div>
          <p>Getting economy data...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import VueApexCharts from "vue3-apexcharts";
import Navigation from '@/components/Navigation.vue';


export default {
  components: {
    apexcharts: VueApexCharts,
    Navigation,
  },
  data() {
    return {
      indexList: [],
      chartOptions: null,
      errorMessage: '',
      loading: false,
      Navigation,
    };
  },
  created() {
    this.chartOptions = {
      chart: { type: 'line', height: 350, zoom: { enabled: true } },
      xaxis: { type: 'datetime' },
      yaxis: {
        labels: {
          formatter: (val) => (val !== null && val !== undefined) ? val.toFixed(2) : '',
        },
      },
      stroke: { width: '2' },
    };
    this.fetchEconomicData();
  },
  methods: {
    async fetchEconomicData() {
     
      const descriptions = {
        "STLFSI4": "Financial Stress Index measures market stress financial system",
        "SP500": "S&P 500 Composite Index represents the U.S. stock market.",
        "HOUST1F": "Single Family Housing Starts measures construction.It plunged prior to the housing bubble burst",
        "UNRATE": "Unemployment Rate indicates joblessness in the economy.",
        "SOFR": "SOFR represents the cost of borrowing between banks. high values mean low level of trust between banks. It was high in 2005 when things began to heat",
        "DRCLACBS":" Delinquency Rate on Consumer Loans, All Commercial Banks. Recession predecesor and An increase signals rising consumer financial stress, potential economic downturns, higher credit risk for banks, and broader economic impacts due to reduced spending and tighter lending conditions",
        "WTREGEN":"Liabilities: Deposits with F.R. Banks, Other Than Reserve Balances.An increase in Liabilities: Deposits with Federal Reserve Banks, Other Than Reserve Balances indicates banks are holding more funds with the Fed instead of lending. This may signal financial stress or uncertainty, leading to reduced lending, potential economic slowdown, and heightened risk aversion in the financial system",
        "DCOILWTICO": "Crude Oil Prices: West Texas Intermediate (WTI) - Cushing, Oklahoma. Measures the daily spot price of WTI crude oil, a benchmark for U.S. oil prices. Significant fluctuations can impact inflation, consumer prices, and economic activity.",
        "WTISPLC": "Spot Crude Oil Price: West Texas Intermediate (WTI). Reflects the immediate market price of WTI crude oil. Trends, volatility, and price movements can signal changes in supply-demand dynamics, global events, and economic health. High volatility may indicate instability, while consistent price rises or falls can signal shifts in market conditions or geopolitical factors.",
        "POILBREUSDM": "Global price of Brent Crude. Represents the monthly average price per barrel of Brent Crude oil, a major global benchmark for oil prices, as determined by the International Monetary Fund. Prices are in nominal U.S. dollars and can indicate global supply-demand dynamics and economic conditions.",
        "PNGASEUUSDM": "Natural Gas Prices in Europe (USD per MMBtu). Represents the price of natural gas in Europe, quoted in U.S. dollars per Million British Thermal Units (MMBtu), providing insights into energy market trends, weather effects, and geopolitical factors that impact supply and demand for natural gas.",
        "PNGASUSUSDM": "Natural Gas Prices in the U.S. (USD per MMBtu). Reflects the price of natural gas in the United States, quoted in U.S. dollars per Million British Thermal Units (MMBtu). This price trend can influence energy consumption, inflation, and the cost of living in the U.S.",
        "MNGLCP": "U.S. Natural Gas Liquid Composite Price. Measures the average price of natural gas liquids (NGLs) in the U.S. NGL",
        "RRPONTSYD": "high value indicates excess liquidity where institutions prefer the safety of parking cash, so check for supportive central bank policies, lower alternative yields, and market caution. Conversely, a low value suggests limited excess cash or redirection to higher-yielding investments; monitor repo rates, broader liquidity metrics, and relevant economic indicators for potential funding stress."
      };
      this.loading = true;
      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/economy_index`);

        // Log the structure to confirm it's correct
        console.log("API Response:", response.data);

        this.indexList = Object.keys(response.data).map(indexID => {
          const observations = response.data[indexID];

          return {
            name: indexID,
            series: [
              {
                name: indexID,
                data: observations.map(item => ({
                  x: new Date(item.date).toISOString(), // Convert date to ISO string
                  y: parseFloat(item.value) // Ensure the value is a float
                }))
              }
            ],
            description: descriptions[indexID] || "No description available.",
          };
        });

        console.log("Processed Index List:", this.indexList);
      } catch (error) {
        this.errorMessage = error.response ? error.response.data : error.message;
        console.error('Error fetching economic data:', this.errorMessage);
      }
      this.loading = false;
    }

  }
 
};
</script>

<style scoped>

.title-container {
  width: 100%;
  text-align: center;
  padding: 20px 0;
}


.chart-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px,10%));
  gap: 10px;
  background: transparent;
}

.chart-box {
  padding: 5px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgb(178, 76, 76);
  transition: transform 0.3s ease;
  background: transparent;
}

.chart-box:hover {
  transform: translateY(-5px);
}

.error-message {
  color: red;
  margin-top: 10px;
}

h1 {

font-size: auto;
margin-bottom: 20px;
margin-left: 10px;
color: #6d6d6d;
text-align: left;
font-weight: bold;

}

p {
  font-size: 0.9em;
  color: rgba(144, 120, 120, 0.977);
  text-align: center;
}
p1 {
  font-size: 0.9em;
  color:white;
  text-align: center;
}
@media (max-width: 768px) {
  .chart-container {
    grid-template-columns: 1fr;
  }
}
</style>