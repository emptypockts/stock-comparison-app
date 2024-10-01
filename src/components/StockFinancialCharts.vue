<template>
  <h1>Charts</h1>
  <div>
    <!-- Display the company names based on the tickers -->
      <div v-if="tickers.length" class="chart-container">

        <!-- Stock Price (Last 5 Years) -->
        <div class="chart-box">
          <h2>Stock Price (Last 5 Years)</h2>
          <apexcharts v-if="stockPriceSeries.length" type="line" :options="chartOptions" :series="stockPriceSeries"></apexcharts>
          <p>This chart shows the stock price movements over the last 5 years.</p>
        </div>

        <!-- Revenue and Assets -->
        <div class="chart-box">
          <h2>Revenue and Assets</h2>
          <apexcharts v-if="revenueAssetsSeries(tickers).length" type="line" :options="chartOptions" :series="revenueAssetsSeries(tickers)"></apexcharts>
          <p>If assets grow faster than revenue, it could mean that inventory is growing fast. It could be a sales forecast warning.</p>
        </div>

        <!-- Cash and Liabilities -->
        <div class="chart-box">
          <h2>Cash and Liabilities</h2>
          <apexcharts v-if="cashLiabilitiesSeries(tickers).length" type="line" :options="chartOptions" :series="cashLiabilitiesSeries(tickers)"></apexcharts>
          <p>Gap between these two could be an indicator of trouble.</p>
        </div>

        <!-- Cash and Net Income -->
        <div class="chart-box">
          <h2>Cash and Net Income</h2>
          <apexcharts v-if="cashNetIncomeSeries(tickers).length" type="line" :options="chartOptions" :series="cashNetIncomeSeries(tickers)"></apexcharts>
          <p>Lower cash flow than net income in high amounts could signal old inventory pile-up or bad debts impacting.</p>
        </div>

        <!-- R&D and Revenue -->
        <div class="chart-box">
          <h2>R&D and Revenue</h2>
          <apexcharts v-if="rdRevenueSeries(tickers).length" type="line" :options="chartOptions" :series="rdRevenueSeries(tickers)"></apexcharts>
          <p>R&D as a percentage of Sales/Revenue.</p>
        </div>

        <!-- Other Expenses -->
        <div class="chart-box">
          <h2>Other Expenses</h2>
          <apexcharts v-if="otherExpensesSeries(tickers).length" type="line" :options="chartOptions" :series="otherExpensesSeries(tickers)"></apexcharts>
          <p>These types of expenses should be non-recurring.</p>
        </div>

        <!-- FCF and Net Income Growth Ratio -->
        <div class="chart-box">
          <h2>FCF and Net Income Growth Ratio</h2>
          <apexcharts v-if="fcfNetIncomeGrowthSeries(tickers).length" type="line" :options="percentageChartOptions" :series="fcfNetIncomeGrowthSeries(tickers)"></apexcharts>
          <p>When not moving at a fairly even pace, this could indicate that net income is not as muscular as it appears.</p>
        </div>

        <!-- Net Income and Basic EPS -->
        <div class="chart-box">
          <h2>Net Income and Basic EPS</h2>
          <apexcharts v-if="netIncomeEPSSeries(tickers).length" type="line" :options="chartOptions" :series="netIncomeEPSSeries(tickers)"></apexcharts>
          <p>EPS diluted takes into account stock options issued to managers but not yet exercised. It also figures in bonds, preferred shares, and stock warrants that can be converted to common stock causing an EPS drop.</p>
        </div>

        <!-- Return on Average Assets -->
        <div class="chart-box">
          <h2>Return on Average Assets</h2>
          <apexcharts v-if="returnOnAssetsSeries(tickers).length" type="line" :options="percentageChartOptions" :series="returnOnAssetsSeries(tickers)"></apexcharts>
          <p>ROA connects the balance sheet to the income statement. Higher than 5% is a healthy figure.</p>
        </div>

        <!-- Cash Dividends Paid Total -->
        <div class="chart-box">
          <h2>Cash Dividends Paid Total</h2>
          <apexcharts v-if="dividendsPaidSeries(tickers).length" type="line" :options="chartOptions" :series="dividendsPaidSeries(tickers)"></apexcharts>
          <p>Dividends should be continuous for the last 5 years.</p>
        </div>
      </div>
      <div v-else>
      <p class="error-message"> {{ errorMessage }}</p>
    </div>
  </div>
</template>

<script>
import axios from 'axios';
import VueApexCharts from "vue3-apexcharts";

export default {
  components: {
    apexcharts: VueApexCharts,
  },
  props: {
    tickers: {
      type: Array,
      required: true,
    },
  },
  data() {
    return {
      financialData: {}, // Object to store multiple tickers' data
      stockPriceData: [], // Array for stock price data
      chartOptions: null,
      percentageChartOptions: null,
      netIncomeEPSChartOptions:null,
      errorMessage: ''
    };
  },
  created(){
    this.netIncomeEPSChartOptions = {
      chart: {
        type: 'line',
        height: 350,
        zoom: {
          enabled: true,
        },
      },
      xaxis: {
        type: 'datetime',
        min: this.chartMinDate,
        max: this.chartMaxDate,
      },
      yaxis: [
        {
          labels: {
            formatter: (val) => {
              if (val === null || val === undefined) return '';
              if (Math.abs(val) >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
              if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
              return `$${val.toFixed(2)}`;
            },
          },
          title: {
            text: 'Net Income',
          },
        },
        {
          opposite: true,
          labels: {
            formatter: (val) => {
              if (val === null || val === undefined) return '';
              return val.toFixed(2); // Format for Basic EPS
            },
          },
          title: {
            text: 'Basic EPS',
          },
        },
      ],
      stroke: {
        width: '2',
      },
    };

    this.chartOptions = {
    chart: {
      type: 'line',
      height: 350,
      zoom: {
        enabled: true,
      },
    },
    xaxis: {
      type: 'datetime',
      min: this.chartMinDate,
      max: this.chartMaxDate,


    },
    yaxis: {
      labels: {
        formatter: (val) => {
          if (val === null || val === undefined) return '';
          if (Math.abs(val) >= 1e9) return `$${(val / 1e9).toFixed(2)}B`;
          if (Math.abs(val) >= 1e6) return `$${(val / 1e6).toFixed(2)}M`;
          return `$${val.toFixed(2)}`;
        },
      },
    },
    stroke: {
      width: '2',
    },
    
  };
  
  this.percentageChartOptions = {
    chart: {
      type: 'line',
      height: 350,
      zoom: {
        enabled: true,
      },
    },
    xaxis: {
      type: 'datetime',
      min: this.chartMinDate,
      max: this.chartMaxDate,
    },
    yaxis: {
      labels: {
        formatter: (val) => {
          if (val === null || val === undefined) return '';
          return `${parseFloat(val).toFixed(2)}%`;
        },
      },
    },
    stroke: {
      width: '2',
    },
  };
},

       
  watch: {
    tickers: {
      immediate: true,
      handler(newTickers) {
        if (newTickers.length) {
          this.fetchCompanyData(newTickers);
        }
      },
    },
  },
  computed: {
  stockPriceSeries() {
    return this.stockPriceData;
  }
},

  methods: {
    
    async fetchCompanyData(tickers) {
      try {
        if (!tickers.length) {
          errorMessage.value = 'Please enter at least one stock ticker.';
          return errorMessage;
        }

        const financialResponse = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/financial_data`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });

        this.financialData = financialResponse.data.financial_data;
        

        const stockPriceResponse = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/stock_price`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });

        this.stockPriceData = Object.keys(stockPriceResponse.data).map(ticker => {
        const datePricePairs = stockPriceResponse.data[ticker];
        return {
          name: `${ticker}`,
          data: Object.entries(datePricePairs).map(([date, price]) => ({
            x: new Date(date).toISOString(), // Convert the date to ISO string format
            y: parseFloat(price) // Ensure the price is a float
            }))
          }
        });console.log("this is the price object",this.datePricePairs)
        console.log("this is how the financial data object looks like:",this.financialData)

      } catch (error) {
        console.error('Error fetching data:', error.response ? error.response.data : error.message);
      }
      
    },
      
    // Functions to handle up to 3 tickers dynamically
    revenueAssetsSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} Revenue`,
          data: data.map(item => ({ x: item.date, y: item.revenue })),
        },
        {
          name: `${ticker} Assets`,
          data: data.map(item => ({ x: item.date, y: item.assets })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },

  cashLiabilitiesSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} Cash`,
          data: data.map(item => ({ x: item.date, y: item.cash })),
        },
        {
          name: `${ticker} Liabilities`,
          data: data.map(item => ({ x: item.date, y: item.liabilities })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },


  cashNetIncomeSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} Cash`,
          data: data.map(item => ({ x: item.date, y: item.cash })),
        },
        {
          name: `${ticker} Net Income`,
          data: data.map(item => ({ x: item.date, y: item.net_income })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },


  rdRevenueSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} R&D`,
          data: data.map(item => ({ x: item.date, y: item.rd })),
        },
        {
          name: `${ticker} Revenue`,
          data: data.map(item => ({ x: item.date, y: item.revenue })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },

  otherExpensesSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} Other Expenses`,
          data: data.map(item => ({ x: item.date, y: item.other_expenses })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },

  fcfNetIncomeGrowthSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} FCF Growth Ratio`,
          data: data.map((item, index, arr) => ({
            x: item.date,
            y: index > 0 ? (item.fcf - arr[index - 1].fcf) / arr[index - 1].fcf : null,
          })),
        },
        {
          name: `${ticker} Net Income Growth Ratio`,
          data: data.map((item, index, arr) => ({
            x: item.date,
            y: index > 0 ? (item.net_income - arr[index - 1].net_income) / arr[index - 1].net_income : null,
          })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },

  netIncomeEPSSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} Net Income`,
          data: data.map(item => ({ x: item.date, y: item.net_income })),
        },
        {
          name: `${ticker} Basic EPS`,
          data: data.map(item => ({ x: item.date, y: item['Basic EPS'] })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },
  returnOnAssetsSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} Return on Assets`,
          data: data.map(item => ({ x: item.date, y: item.return_on_assets })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },

  dividendsPaidSeries() {
    return this.tickers.map(ticker => {
      const data = this.financialData[ticker] || [];
      return [
        {
          name: `${ticker} Dividends Paid`,
          data: data.map(item => ({ x: item.date, y: item.dividends_paid })),
        }
      ];
    }).flat(); // Flatten to combine series from all tickers into one array
  },
  },
};
</script>
<style scoped>
.error-message {
  color: red;
  margin-top: 10px;
}
.stock-financial-charts {
  padding: 20px;
  background-color: #f8f9fa;
  color: #333;
  max-width: 1200px;
  margin: 0 auto;
}

h1 {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #333;
  text-align: left;
  font-weight: bold;
}

h2 {
  font-size: 1.5em;
  margin-bottom: 10px;
  color: #555;
}

p {
  font-size: 0.9em;
  color: #666;
  margin-top: 5px;
}

.chart-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 20px;
}

.chart-box {
  background-color: #fff;
  padding: 20px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.chart-box:hover {
  transform: translateY(-5px);
}

apexcharts {
  max-width: 100%;
  margin: 0 auto;
}

@media (max-width: 768px) {
  .stock-financial-charts {
    padding: 10px;
  }

  h1 {
    font-size: 2em;
  }

  h2 {
    font-size: 1.2em;
  }

  p {
    font-size: 0.8em;
  }

  .chart-box {
    padding: 15px;
  }
}
</style>