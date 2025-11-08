<template>
  <h1 class="app-title">Ticker Data 
  </h1>    
  <div class="input-container">
    <input v-model="ticker1" placeholder="@ticker1" id="ticker 1" />
  </div>
  <div>
    <button @click="verifyAndFetchCompanyData">Analyse</button>
  </div>
  <!-- Error message display -->
  <div v-if="errorMessage" class="error-message">
    <p>{{ errorMessage }}</p>
  </div>
    
  <div>
    <div v-if="companyData">
      <ul class="list-container">
        
        <li v-for="(e,ticker) in companyData" :key="ticker">
          <strong>
            Company:
          </strong> 
            {{ e.gStockData.symbol }}: {{ e.gStockData.name }}. 
            <strong>
            Current price:
          </strong> 
          ${{ e.gStockData.current_price}} 
          <strong>
            Last Filing :
          </strong> {{ e.last_filing_date  }}
          <br><br>
        </li>
      </ul>
      </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; // Import useRouter for navigation
import debounce from 'lodash.debounce';
import { useLoadingStore } from '@/stores/loadingStore';
import { verifyCfToken, verifyToken } from '@/utils/auth';
import { useTickerStore } from '@/stores/tickerStore';
import { showTempMessage } from '@/utils/timeout';
  const emit = defineEmits(['tickers-updated']);
    const errorMessage = ref('');
    const ticker1 = ref('');
    const ticker2 = ref('');
    const ticker3 = ref('');
    const loading = useLoadingStore();
    const companyData = ref({});
    const tickerStore=useTickerStore()
    const fetchCompanyData = debounce(async () => {

      const tickers = [ticker1, ticker2, ticker3].map(tickerRef => tickerRef.value).filter(Boolean);
      if (tickers.length === 0) {
        showTempMessage(errorMessage, 'Please enter at least one stock ticker.', 2000);
        return errorMessage;
      }
      errorMessage.value = ""

      loading.startLoading();
      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/company_data`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });
        companyData.value = response.data;
        if (!companyData.value || Object.keys(companyData.value).length === 0) {
          errorMessage.value = 'No data found. this app is doing data collection of american companies only';
          showTempMessage(errorMessage, 'No data found for the entered tickers.', 2000);

        } else {
          
          const missingTickers = tickers.filter(
            ticker => !Object.keys(companyData.value).includes(ticker)
          );
          if (missingTickers.length > 0) {
            showTempMessage(errorMessage, `Data for the following tickers is missing: ${missingTickers.join(', ')}.
            this app is doing data collection for american companies only.`, 5000);
          }
        }
        console.log("companyData",companyData)
        tickerStore.updateTickers(tickers)
        emit('tickers-updated', tickers);
        
      } catch (error) {
        console.error("error trying to fetch company data", error)
        return errorMessage;
      }

      finally {

        loading.stopLoading();

      }
    },600);
    // Wrapper function to verify the token before fetching company names
    const verifyAndFetchCompanyData = async () => {
      const isTokenValid = await verifyCfToken();
      
      if (isTokenValid) {
        fetchCompanyData();
      }
    };
</script>
<style scoped>
.error-message {
  color: red;
  margin-top: 10px;
}

.loading-section {
  width: auto;
  height: auto;
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 15px;
  color: white;
  font-size: 1.5em;
  z-index: 1000;

}

.input-container{
width: auto;
margin-left: 10px;
background: transparent;

}

input {
  width: auto;
  padding: 8px;
  margin-top: 5px;
  border-radius: 8px;
  border: 1px solid #f1f0f0;
  background-color: #adadad1c;
  row-gap: 10px;
  display: flex;
}

input::placeholder {
  background-color: transparent;
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
  margin-left: 10px;
}

button:hover {
  background-color: #468eda;
}


ul {
  list-style-position: inside;
  /* Moves the bullet inside the content box */
  padding-left: 0;
  /* Removes additional padding */

}

.list-container {
  border-radius: 8px;
  width: 90%;
}

li {

  margin-left: 0;
  /* Ensure no left margin */
  padding-left: 0;
  /* Remove any extra padding on the left */


}

</style>