<template>
  <div class="input-row">
    <span style="color: red;">eacsa></span><span style="color: gray;"> ticker:</span>

    <input 
    v-model="ticker1"
    id="ticker 1" 
    class="terminal-input" 
    @keyup.enter="verifyAndFetchCompanyData"
    />
                <button 
                :disabled="loading.isLoading" 
                @click="verifyAndFetchCompanyData" 
                class="buttons">
            {{loading['isLoading'] ? 'generating report': 'fundamentals'}}
            </button>
            </div>
  
  <div>
    <div v-if="tickerList.length > 0">
      <div class="terminal">
        <span>eacsa> </span>company details:
      </div>
      <ul class="list-container">
        <li v-for="(e, ticker) in companyData" :key="ticker">
          <strong>
            Company:
          </strong>
          {{ e.gStockData.symbol }}: {{ e.gStockData.name }}.
          <strong>
            Current price:
          </strong>
          ${{ e.gStockData.current_price }}
          <strong>
            Last Filing :
          </strong> {{ e.last_filing_date }}
        </li>
      </ul>
    </div>
  </div>
  <!-- Error message display -->
      <div v-if="notification" :class="['msg', notification.type]">
        {{ notification.text}}
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
import { showTempMessage } from '@/utils/showMessages';
import { fetch_reports, ai_reports } from '@/utils/fetch_reports';
const emit = defineEmits(['tickers-updated']);
const notification = ref(null);
const ticker1 = ref('');
const ticker2 = ref('');
const ticker3 = ref('');
const loading = useLoadingStore();
const companyData = ref({});
const tickerStore = useTickerStore()
const tickerList = ref([])
const fetchCompanyData = debounce(async () => {

  const tickers = [ticker1, ticker2, ticker3].map(tickerRef => tickerRef.value).filter(Boolean);
  tickerList.value = tickers
  if (tickers.length === 0) {
    showTempMessage(notification, 'Please enter a ticker',"error");
    return notification;
  }

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
      showTempMessage(notification, 'No data found for the entered tickers.',"error");

    } else {

      const missingTickers = tickers.filter(
        ticker => !Object.keys(companyData.value).includes(ticker)
      );
      if (missingTickers.length > 0) {
        showTempMessage(notification, `Data for the following tickers is missing: ${missingTickers.join(', ')}.
            this app is doing data collection for american companies only.`,"error");
      }
    }
    tickerStore.updateTickers(tickers)
    emit('tickers-updated', tickers);

  } catch (error) {
    console.error("error trying to fetch company data", error)
    return notification;
  }

  finally {

    loading.stopLoading();

  }
}, 600);

// Wrapper function to verify the token before fetching company names
const verifyAndFetchCompanyData = async () => {
  const isTokenValid = await verifyCfToken();

  if (isTokenValid) {
    fetchCompanyData();
  }
};
</script>
<style scoped></style>