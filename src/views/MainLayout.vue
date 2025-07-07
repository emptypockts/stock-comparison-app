<template>
    <h1 class="app-title">Welcome to Honcho</h1>
    <CompanyData @tickers-updated="updateTickers" />
    <ValueStockAnalysis :tickers="tickers" />
    <StockFinancialCharts :tickers="tickers" />
    <IntrinsicValue :tickers="tickers" />
    <RittenhouseAnalysis Analyis :tickers="tickers" />
    <Navigation />
    <CookieBanner />
    <LoginAlert />
    <button :disabled="tickers.length === 0" @click="get_report">ai report</button>
    <small> ⚠️warning it takes around 40 sec per ticker <br></small>
    <div v-if="tickerHistory.size > 0">
        <small>
            <strong>ticker history:</strong> {{[...tickerHistory].join(',')}}
            </small>
    </div>
    <div class="error-message">
        {{ errorMessage }}
    </div>

</template>
<script setup>
import { ref, watch } from 'vue';
import IntrinsicValue from '@/views/IntrinsicValue.vue';
import CompanyData from '@/views/CompanyData.vue';
import StockFinancialCharts from '@/views/StockFinancialCharts.vue';
import ValueStockAnalysis from '@/views/ValueStockAnalysis.vue';
import RittenhouseAnalysis from "@/views/RittenhouseAnalysis.vue";
import { useTickerStore } from '@/stores/tickerStore';
import Navigation from '@/components/Navigation.vue';
import CookieBanner from '@/components/CookieBanner.vue';
import LoginAlert from '@/components/LoginAlert.vue';
import { showTempMessage } from '@/utils/timeout';
import { useLoadingStore } from '@/stores/loadingStore';
import axios from 'axios';
import { downloadPdfReport } from '@/utils/downloadReport';
import { taskSocket } from '@/composables/taskSocket';

const tickers = ref([]);
const errorMessage = ref('');
const tickerStore = useTickerStore();
const loading = useLoadingStore();
const tickerHistory = ref(new Set());
const allowedTickers=ref([]);
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
        
        allowedTickers.value=tickers.value.filter(e=>!tickerHistory.value.has(e.toLowerCase()))
        
        if (allowedTickers.value.length>0) {
            loading.startLoading();
            const user_id = localStorage.getItem('user_id')
            try {
                const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini`, {
                    tickers: allowedTickers.value,
                    user_id:user_id
                })
                
                const task_id = response.task_id;

                taskSocket(task_id,async (assistant)=>{
                    console.log('task completed calling from mainlayout, calling pdf api',assistant)
                    await downloadPdfReport(assistant, tickers.value, "overall")
                })

                
                


            }




            catch (err) {
                console.error('error trying to generate report:', err)

            }
            finally {
                loading.stopLoading();
                tickers.value.forEach(t=>tickerHistory.value.add(t.toLowerCase()));
                
            }


        }
        else{
        
        errorMessage.value = 'ticker previously analysed. refresh your broweser if you need to analyse it again'
        showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 2000);
    }
    }
    

}
</script>
<style>
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
