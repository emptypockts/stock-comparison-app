<template>
  <div>
    <h1>Ticker Data</h1>
    <input v-model="ticker1" placeholder="Enter Stock Ticker 1" />
    <input v-model="ticker2" placeholder="Enter Stock Ticker 2 (Optional)" />
    <input v-model="ticker3" placeholder="Enter Stock Ticker 3 (Optional)" />
    <button @click="fetchCompanyNames">Analyse Stock</button>
  </div>
  <div>
  <h1>Company</h1>
    <div v-if="companyNames">
      <ul>
        <li v-for="(name, ticker) in companyNames" :key="ticker">
          {{ ticker }}: {{ name[0] }}. Current price: ${{ name[1] }} <br>Next Earnings Date: {{ name[2] }}
        </li>
      </ul>
    </div>
    <div v-else>
      <p>No company names found</p>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
export default {
  emits: ['tickers-updated','loading'], // Declare the custom events
  setup(props, { emit }) {
    const ticker1 = ref('');
    const ticker2 = ref('');
    const ticker3 = ref('');
    const companyNames = ref({});
    const fetchCompanyNames = async()=> {
      const tickers = [ticker1, ticker2,ticker3].map(tickerRef => tickerRef.value).filter(Boolean);
      if (tickers.length === 0) {
        alert('Please enter at least one stock ticker.');
        return;
      }
      // Emit loading status as true to indicate loading has started
      emit('loading', true);
      
      console.log("tickers:",tickers)
      // await new Promise(resolve => setTimeout(resolve, 3000)); // 3-second delay
      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/company_name`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });
        
        
        companyNames.value = response.data;
        console.log("Company Names Object:",companyNames.value)
        const unknownCompany = Object.values(companyNames).includes('Unknown');
        if (unknownCompany) {
          alert('One or more ticker symbols are invalid. Please check your input.');
          emit('loading', false); // Emit loading status as false to stop loading
          return; // Stop further processing
        }

        // Emit the tickers and company names to the parent component
        emit('tickers-updated', tickers);
      } catch (error) {
        console.error('Error fetching company names:', error);
        alert('An error occurred while fetching company names.');
      }
      
      finally {
        // Emit loading status as false to stop loading after the request is complete
        emit('loading', false);
      }
    };
    return {
      ticker1,
      ticker2,
      ticker3,
      fetchCompanyNames,
      companyNames,
    };
  },
};
</script>
<style scoped>
.loading-section{
width: auto;
height: auto;
display: flex;
align-items: center;
background-color:rgba(0, 0, 0, 0.5);
border-radius: 15px;
color: white;
font-size: 1.5em;
z-index: 1000;

}
</style>