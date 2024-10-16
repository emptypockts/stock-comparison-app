<template>
  <div class="page">
    <h1>Economic Indicators</h1>
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
      <Logout/>
      <BotLogo/>  
      <economyIdxLogo/>
      <GoBack/>
      </div>
      <div v-if="loading" class="loading-overlay">
        <div class="loading-throbber">
          <div class="spinner"></div>
          <p>Getting eonomy data. Please wait...</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import VueApexCharts from "vue3-apexcharts";
import GoBack from './goBack.vue';
import Logout from './Log_out.vue';
import BotLogo from './botLogo.vue';
import economyIdxLogo from './economyIdxLogo.vue';


export default {
  components: {
    apexcharts: VueApexCharts,
    GoBack,
    Logout,
    BotLogo,
    economyIdxLogo,
  },
  data() {
    return {
      indexList: [],
      chartOptions: null,
      errorMessage: '',
      loading: false,
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
      const indexIDs = ["STLFSI4", "SP500", "HOUST1F", "UNRATE", "SOFR","DRCLACBS","WTREGEN"];
      const descriptions = {
        "STLFSI4": "Financial Stress Index measures market stress financial system",
        "SP500": "S&P 500 Composite Index represents the U.S. stock market.",
        "HOUST1F": "Single Family Housing Starts measures construction.It plunged prior to the housing bubble burst",
        "UNRATE": "Unemployment Rate indicates joblessness in the economy.",
        "SOFR": "SOFR represents the cost of borrowing between banks. high values mean low level of trust between banks. It was high in 2005 when things began to heat",
        "DRCLACBS":" Delinquency Rate on Consumer Loans, All Commercial Banks. Recession predecesor and An increase signals rising consumer financial stress, potential economic downturns, higher credit risk for banks, and broader economic impacts due to reduced spending and tighter lending conditions",
        "WTREGEN":"Liabilities: Deposits with F.R. Banks, Other Than Reserve Balances.An increase in Liabilities: Deposits with Federal Reserve Banks, Other Than Reserve Balances indicates banks are holding more funds with the Fed instead of lending. This may signal financial stress or uncertainty, leading to reduced lending, potential economic slowdown, and heightened risk aversion in the financial system",
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
.page {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  align-items: center;
  width: 100%;
  height: 100%;
  background: repeat center url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=2225&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
  background-size: auto;
  padding: 20px;
  box-sizing: border-box;
  background: transparent;
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
  box-shadow: 0 4px 8px rgb(111, 80, 80);
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

h2 {
  font-size: 1.5em;
  margin-bottom: 10px;
  color: #555;
}

p {
  font-size: 0.9em;
  color: #666;
  text-align: center;
}

@media (max-width: 768px) {
  .chart-container {
    grid-template-columns: 1fr;
  }
}
</style>