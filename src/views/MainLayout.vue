<template>
    <h1 class="app-title">Honcho Financials®</h1>
    <div class="container">
        <h1 class="app-title">
            Financials Overview
        </h1>

        <CompanyData @tickers-updated="updateTickers" />
        <ValueStockAnalysis :tickers="tickers" />
        <StockFinancialCharts :tickers="tickers" />
        <IntrinsicValue :tickers="tickers" />


        <button :disabled="tickers.length === 0" @click="get_report">Analyse with ai</button>
        <small> ⚠️warning it takes around 40 sec per ticker <br></small>
        <div v-if="tickerHistory.size > 0">
            <small>
                <strong>ticker history:</strong> {{ [...tickerHistory].join(',') }}
            </small>
        </div>
                  <div>
    <p v-if="isConnected">🟢 ai analysis available</p>
    <p v-else>🔴 ai analysis not available</p>
  </div>
        <div class="error-message">
            {{ errorMessage }}
        </div>
    </div>
    <div class="container">
        <h2 class="app-title">
            Framework and AI Analysis
        </h2>
        <RittenhouseAnalysis Analysis :tickers="tickers" />
        <AI Analysis :tickers="tickers" />
                  <div>
    <p v-if="isConnected">🟢 ai analysis available</p>
    <p v-else>🔴 ai analysis not available</p>
  </div>
    </div>
    <Navigation />
    <CookieBanner />
    <LoginAlert />



</template>
<script setup>
import { ref, watch } from 'vue';
import IntrinsicValue from '@/views/IntrinsicValue.vue';
import CompanyData from '@/views/CompanyData.vue';
import StockFinancialCharts from '@/views/StockFinancialCharts.vue';
import ValueStockAnalysis from '@/views/ValueStockAnalysis.vue';
import RittenhouseAnalysis from "@/views/RittenhouseAnalysis.vue";
import AI from "@/views/AI.vue"
import { useTickerStore } from '@/stores/tickerStore';
import Navigation from '@/components/Navigation.vue';
import CookieBanner from '@/components/CookieBanner.vue';
import LoginAlert from '@/components/LoginAlert.vue';
import { showTempMessage } from '@/utils/timeout';
import { useLoadingStore } from '@/stores/loadingStore';
import { useSocket } from '@/composables/taskSocket';
import axios from 'axios';
const isConnected=useSocket()
const tickers = ref([]);
const errorMessage = ref('');
const tickerStore = useTickerStore();
const loading = useLoadingStore();
const tickerHistory = ref(new Set());
const allowedTickers = ref([]);
const updateTickers = (newTickers) => {
    tickerStore.updateTickers(newTickers)
    tickers.value = tickerStore.currentTickers
}



const get_report = async () => {
    if (tickers.value.length == 0) {
        console.error('missing tickers');
        errorMessage.value = 'enter at least 1 ticker and analyse it to enable the ai report'
        showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 2000);
    }
    else {
        allowedTickers.value = tickers.value.filter(e => !tickerHistory.value.has(e.toLowerCase()))

        if (allowedTickers.value.length > 0 && isConnected) {
            loading.startLoading();
            const user_id = localStorage.getItem('user_id')
            try {
                const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini`, {
                    tickers: allowedTickers.value,
                    user_id: user_id,
                    report_type: "overall"
                })
            }




            catch (err) {
                console.error('error trying to generate report:', err)

            }
            finally {
                tickers.value.forEach(t => tickerHistory.value.add(t.toLowerCase()));

            }


        }
        else {

            errorMessage.value = 'ticker previously analysed. refresh your broweser if you need to analyse it again'
            showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 2000);
        }
    }


}
</script>
<style>
.container {
    box-shadow:
        0 1px 2px rgba(0, 0, 0, 0.08),
        0 4px 6px rgba(0, 0, 0, 0.1),
        0 10px 15px rgba(0, 0, 0, 0.08);
    border-radius: 1rem;
    /* rounded corners */
    background: #f8f3f3;
}

.error-message {
    color: red;
    margin-top: 10px;
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

button:disabled {
    background-color: #999;
    /* Gray out */
    opacity: 0.6;
    /* Faded */
    cursor: not-allowed;
    /* Show "blocked" cursor */
}
</style>
