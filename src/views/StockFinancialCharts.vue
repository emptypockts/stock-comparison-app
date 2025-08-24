<template>
  <h1>Charts</h1>
  <div>
    <button @click="toggleView">
      {{ isYearlyView ? "Switch to Quartetly View" : "Switch to Yearly View" }}

    </button>
  </div>
  <div>
    <!-- Display the company names based on the tickers -->
    <div v-if="tickers.length" class="chart-container">
      <!-- Stock Price (Last 5 Years) -->
      <div class="chart-box">
        <h2>{{isYearlyView? "Stock Price (Last 5 Years)":"Stock Price (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="pickStockPriceSeries.length" type="line" :options="chartOptionsPrice" :series="pickStockPriceSeries">
        </apexcharts>
        <p>This chart shows the stock price movements.</p>
      </div>
      <!-- Revenue and Assets -->
      <div class="chart-box">
        <h2>{{isYearlyView? "Revenue and Assets (Last 5 Years)":"Revenue and Assets (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="pickRevenueAssetsSeries.length" type="line" :options="chartOptions" :series="pickRevenueAssetsSeries"></apexcharts>
        <p>If assets grow faster than revenue, it could mean that inventory is growing fast. It could be a sales
          forecast warning.</p>
      </div>
      <!-- Cash and Liabilities -->
      <div class="chart-box">
        <h2>{{isYearlyView? "Cash and Liabilities (Last 5 Years)":"Cash and Liabilities (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="pickCashLiabilitiesSeries.length" type="line" :options="chartOptions"
          :series="pickCashLiabilitiesSeries"></apexcharts>
        <p>Gap between these two could be an indicator of trouble.</p>
      </div>

      <!-- Cash and Net Income -->
      <div class="chart-box">
        <h2>{{isYearlyView? "Cash and Net Income (Last 5 Years)":"Cash and Net Income (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="pickCashNetIncomeSeries.length" type="line" :options="chartOptions"
          :series="pickCashNetIncomeSeries"></apexcharts>
        <p>Lower cash flow than net income in high amounts could signal old inventory pile-up or bad debts impacting.
        </p>
      </div>

      <!-- R&D and Revenue -->
      <div class="chart-box">
        <h2>{{isYearlyView? "R&D and Revenue (Last 5 Years)":"R&D and Revenue (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="pickRdRevenueSeries.length" type="line" :options="chartOptions"
          :series="pickRdRevenueSeries"></apexcharts>
        <p>R&D as a percentage of Sales/Revenue.</p>
      </div>

      <!-- Other Expenses -->
      <div class="chart-box">
        <h2>{{isYearlyView?"Other Expenses (Last 5 Years)":"Other Non Current Liabilities (Last q Quarters)"}}</h2>
        <apexcharts v-if="pickOtherExpensesSeries.length" type="line" :options="chartOptions"
          :series="pickOtherExpensesSeries"></apexcharts>
        <p>These types of expenses should be non-recurring.</p>
      </div>

      <!-- FCF and Net Income Growth Ratio -->
      <div class="chart-box">
        <h2>{{isYearlyView? "FCF Net Income Growth % (Last 5 Years)":"FCF Net Income Growth % (Last 4 Quarters)"}} </h2>
        <apexcharts v-if="pickFcfNetIncomeGrowthSeries.length" type="line" :options="percentageChartOptions"
          :series="pickFcfNetIncomeGrowthSeries"></apexcharts>
        <p>When not moving at a fairly even pace, this could indicate that net income is not as muscular as it appears.
        </p>
      </div>

      <!-- Basic EPS -->
      <div class="chart-box">
        <h2>{{isYearlyView? "Basic EPS (Last 5 Years)":"Basic EPS (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="PickEPSSeries.length" type="line" :options="chartOptions"
          :series="PickEPSSeries"></apexcharts>
        <p>EPS diluted takes into account stock options issued to managers but not yet exercised. It also figures in
          bonds, preferred shares, and stock warrants that can be converted to common stock causing an EPS drop.</p>
      </div>

      <!-- Return on Average Assets -->
      <div class="chart-box">
        <h2>{{isYearlyView? "Return on Average Assets (Last 5 Years)":"Return on Average Assets (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="pickReturnOnAssetsSeries.length" type="line" :options="percentageChartOptions"
          :series="pickReturnOnAssetsSeries"></apexcharts>
        <p>ROA connects the balance sheet to the income statement. Higher than 5% is a healthy figure.</p>
      </div>

      <!-- Cash Dividends Paid Total -->
      <div class="chart-box">
        <h2>{{isYearlyView?"Cash Dividends Paid Total (Last 5 Years)":"Cash Dividends Paid Total (Last 4 Quarters)"}}</h2>
        <apexcharts v-if="pickDividendsPaidSeries.length" type="line" :options="chartOptions"
          :series="pickDividendsPaidSeries"></apexcharts>
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
import { useLoadingStore } from '@/stores/loadingStore';
export default {
  
  components: {
    apexcharts: VueApexCharts,
  },
  props: {
    tickers: {
      type: Array
    },
  },
  data() {
    const loading = useLoadingStore();
    return {
      financialData: {}, // Object to store multiple tickers' data
      stockPriceData: [], // Array for stock price data
      chartOptions: null,
      chartOptionsPrice:null,
      percentageChartOptions: null,
      EPSChartOptions: null,
      errorMessage: '',
      isYearlyView: true,
      financialDataQtr: {},
      stockPriceDataQtr:[],
      loading

    }; 
  },
  created() {
    this.EPSChartOptions = {
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
    this.chartOptionsPrice = {
      chart: {
        type: 'line',
        height: 350,
        zoom: {
          enabled: true,
        },
      },
      xaxis: {
        type: 'string',
      

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
    this.ratioChartOptions = {
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
            return `${parseFloat(val).toFixed(2)}`;
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
    pickStockPriceSeries() {
      return this.isYearlyView ? this.stockPriceData : this.stockPriceDataQtr;  
    },
    pickRevenueAssetsSeries() {
      return this.isYearlyView ? this.revenueAssetsSeries() : this.revenueAssetsSeriesQtr();
    },
    pickCashLiabilitiesSeries() {
      return this.isYearlyView ? this.cashLiabilitiesSeries() : this.cashLiabilitiesSeriesQtr();
    },
    pickCashNetIncomeSeries() {
      return this.isYearlyView ? this.cashNetIncomeSeries() : this.cashNetIncomeSeriesQtr();
    },
    pickRdRevenueSeries() {
      return this.isYearlyView ? this.rdRevenueSeries() : this.rdRevenueSeriesQtr();
    },
    pickOtherExpensesSeries() {
      return this.isYearlyView ? this.otherExpensesSeries() : this.OtherNonCurrentLiabilities();
    },
    pickFcfNetIncomeGrowthSeries() {
      return this.isYearlyView ? this.fcfNetIncomeGrowthSeries() : this.fcfNetIncomeGrowthSeriesQtr();
    },
    PickEPSSeries() {
      return this.isYearlyView ? this.EPSSeries() : this.EPSSeriesQtr();
    },
    pickReturnOnAssetsSeries() {
      return this.isYearlyView ? this.returnOnAssetsSeries() : this.returnOnAssetsSeriesQtr();
    },
    pickDividendsPaidSeries() {
      return this.isYearlyView ? this.dividendsPaidSeries() : this.dividendsPaidSeriesQtr();
    },

  },
  methods: {
    toggleView(){
    this.isYearlyView= !this.isYearlyView;
    },
    async fetchCompanyData(tickers) {
      this.loading.startLoading();
      try {
        if (!tickers.length) {
          this.errorMessage = 'Please enter at least one stock ticker.';
          return this.errorMessage;
        }
        const financialResponseQtr = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/financial_data_qtr`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });
        const financialResponse = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/financial_data`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });
        this.financialData = financialResponse.data.financial_data;
        this.financialDataQtr=financialResponseQtr;
        const stockPriceResponse = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/stock_price`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}), 
        });
        const currentDate = new Date(); 
      const twelveMonthsAgo = new Date();
      twelveMonthsAgo.setFullYear(currentDate.getFullYear() - 1); // Set to 12 months ago


      this.stockPriceDataQtr = Object.keys(stockPriceResponse.data).map(ticker => {
          const datePricePairs = stockPriceResponse.data[ticker];
          return {
            name: `${ticker}`,
            data: Object.entries(datePricePairs)
            .filter(([date])=>new Date(date)>=twelveMonthsAgo)
            .map(([date, price]) => ({
              x: new Date(date).toISOString(), // Convert the date to ISO string format
              y: parseFloat(price) // Ensure the price is a float
            }))
          }
        }); 
      this.stockPriceData=stockPriceResponse.data.map(e=>{
          const [ticker,values]=Object.entries(e)[0]
          
          return{
            name:ticker,
            data:
              Object.entries(values).sort(([a],[b])=>Number(a)-Number(b)).map(([year,price])=>({
                x:year,
                y:price
              }))
              
            
          }
        })
      } catch (error) {
        this.errorMessage = error.response ? error.response.data : error.message; // Update here
        console.error('Error fetching data:', error.response ? error.response.data : error.message);
      }
      finally{
        this.loading.stopLoading();
      }
    },
    // Functions to handle up to 3 tickers dynamically
    revenueAssetsSeriesQtr() {
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const assets = financialData["Assets"] ||{x:'1900-01-01',y:0};
        const totalRevenue = financialData["total_revenue"] ||{x:'1900-01-01',y:0};
        
        return [
          {
            name: `${ticker} Total Revenue`,
            data: Object.entries(totalRevenue).map(([date, value]) => ({x:date,y:value})),
          },
          {
            name: `${ticker} Assets`,
            data: Object.entries(assets).map(([date, value])=> ({x:date,y:value})),
          }
        ];
      }).flat(); // Flatten to combine series from all tickers into one array
    },
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
    cashLiabilitiesSeriesQtr(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const cash = financialData["CashAndCashEquivalentsAtCarryingValue"] || {x:'1900-01-01',y:0};
        const liabilities = financialData["Liabilities"] || {x:'1900-01-01',y:0};
        return [
          {
            name: `${ticker} Cash`,
            data: Object.entries(cash).map(([date, value]) => ({x:date,y:value})),
          },
          {
            name: `${ticker} Liabilities`,
            data: Object.entries(liabilities).map(([date, value])=> ({x:date,y:value})),
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
    cashNetIncomeSeriesQtr(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const cash = financialData["CashAndCashEquivalentsAtCarryingValue"] ||{x:'1900-01-01',y:0};
        const NetIncomeLoss = financialData["NetIncomeLoss"] ||{x:'1900-01-01',y:0};
        return [
          {
            name: `${ticker} Cash`,
            data: Object.entries(cash).map(([date, value]) => ({x:date,y:value})),
          },
          {
            name: `${ticker} Net Income Loss`,
            data: Object.entries(NetIncomeLoss).map(([date, value])=> ({x:date,y:value})),
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
    rdRevenueSeriesQtr(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const rD = financialData["ResearchAndDevelopmentExpense"] ||{x:'1900-01-01',y:0};
        const totalRevenue = financialData["total_revenue"] ||{x:'1900-01-01',y:0};
        return [
          {
            name: `${ticker} R&D`,
            data: Object.entries(rD).map(([date, value]) => ({x:date,y:value})),
          },
          {
            name: `${ticker} Revenue`,
            data: Object.entries(totalRevenue).map(([date, value])=> ({x:date,y:value})),
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
    OtherNonCurrentLiabilities(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const OtherLiabilitiesNoncurrent = financialData["OtherLiabilitiesNoncurrent"] ||{x:'1900-01-01',y:0};
        return [
          {
            name: `${ticker} Other Non Current Liabilities`,
            data: Object.entries(OtherLiabilitiesNoncurrent).map(([date, value]) => ({x:date,y:value})),
          },
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
    fcfNetIncomeGrowthSeriesQtr(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const fcf = financialData["fcf"] ||{x:'1900-01-01',y:0};
        const NetIncomeLoss = financialData["NetIncomeLoss"] ||{x:'1900-01-01',y:0};
        return [
          {
            name:`${ticker} FCF Growth Ratio`,
            data:Object.keys(fcf).map((date,index,arr)=>({
            x:date,
            y:index > 0 ? (fcf[date] - fcf[arr[index - 1]]) / fcf[arr[index - 1]] : null
          })).flat(),
 
          },
          {
            name:`${ticker} Net Income Growth Ratio`,
            data:Object.keys(NetIncomeLoss).map((date,index,arr)=>({
              x:date,
            y:index > 0 ? (NetIncomeLoss[date] - NetIncomeLoss[arr[index - 1]]) / NetIncomeLoss[arr[index - 1]] : null
          })).flat(),
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
    EPSSeriesQtr(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const EarningsPerShareBasic = financialData["EarningsPerShareBasic"] ||{x:'1900-01-01',y:0};
        return [
          {
            name: `${ticker} EarningsPerShareBasic`,
            data: Object.entries(EarningsPerShareBasic).map(([date, value]) => ({x:date,y:value})),
          },
        ];
      }).flat(); // Flatten to combine series from all tickers into one array
    },
    EPSSeries() {
      return this.tickers.map(ticker => {
        const data = this.financialData[ticker] || [];
        return [
          // removed because it is already plotted in another chart.
          // {
          //   name: `${ticker} Net Income`,
          //   data: data.map(item => ({ x: item.date, y: item.net_income })),
          // },
          {
            name: `${ticker} Basic EPS`,
            data: data.map(item => ({ x: item.date, y: item['Basic EPS'] })),
          }
        ];
      }).flat(); // Flatten to combine series from all tickers into one array
    },
    returnOnAssetsSeriesQtr(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const return_on_assets = financialData["return_on_assets"] ||{x:'1900-01-01',y:0};
        return [
          {
            name: `${ticker} return_on_assets`,
            data: Object.entries(return_on_assets).map(([date, value]) => ({x:date,y:value})),
          },
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
    dividendsPaidSeriesQtr(){
      return this.tickers.map(ticker => {
        const financialData = this.financialDataQtr.data[ticker]?.['financial_data_qtr'] ||{x:'1900-01-01',y:0};
        const PaymentsOfDividends = financialData["PaymentsOfDividends"] ||{x:'1900-01-01',y:0};
        return [
          {
            name: `${ticker} PaymentsOfDividends`,
            data: Object.entries(PaymentsOfDividends).map(([date, value]) => ({x:date,y:value})),
          },
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
char .error-message {
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
  margin-top: 5px;
}

.chart-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 10%));
  gap: 10px;
  background-color: transparent;
}

.chart-box {
  background-color: transparent;
  padding: 5px;
  border-radius: 10px;
  box-shadow: 0 4px 8px rgb(111, 80, 80);
  transition: transform 0.3s ease;
}

.chart-box:hover {
  transform: translateY(-5px);
}



@media (max-width: 768px) {
  .stock-financial-charts {
    padding: 10px;
  }

  p {
    font-size: 0.8em;
  }

}

button {
  position: relative;
  width: auto;
  justify-content: left;
  padding: 8px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
  background-color: #8bb4e0;
  margin-right: 10px;
}

button:hover {
    background-color: #468eda;
}
</style>