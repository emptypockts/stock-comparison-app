<template>
    <div>
        <div>
            <h1 class="app-title">Hamilton H's Seven Powers.</h1>
        </div>
        <button @click="get_seven_p_analysis">
        7powers ai report
        </button>
        <small> ⚠️warning it takes around 30 sec per ticker <br></small>
        <div>
            <Navigation />
        </div>
        <div v-if="tickerHistory.size > 0">
            <small>
                <strong>ticker history:</strong> {{ [...tickerHistory].join(',') }}
            </small>
        </div>
    <div>
    <p v-if="isConnected">🟢 ai analysis available</p>
    <p v-else>🔴 ai analysis not available</p>
  </div>
    </div>

</template>

<script setup>
import { ref, computed } from 'vue';
import Navigation from '@/components/Navigation.vue';
import axios from 'axios';
import { useTickerStore } from '@/stores/tickerStore';
import { useLoadingStore } from '@/stores/loadingStore';
import CompanyData from './CompanyData.vue';
import {useSocket} from '@/composables/taskSocket'
const {isConnected, taskData}=useSocket();
const rawMessage = ref('');
const tickerHistory = ref(new Set())
const tickerStore = useTickerStore();
const loading = useLoadingStore();
const allowedTickers = ref([]);
const tickers = ref([]);

const isLoading = computed(()=>loading.isLoading)






const messages = ref([
    { text: 'I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start. ', isUser: false }
]);

async function get_seven_p_analysis() {
    tickers.value = tickerStore.currentTickers
    const user_id = localStorage.getItem('user_id')

    if (tickers.length === 0) {

        messages.value.push({
            text: 'ticker analysis is empty. there must be an analysis and 7powers analysis generated first',
            isUser: false
        })

    }
    else {
        if (tickers.value.length > 0) {

            allowedTickers.value = tickers.value.filter(e => !tickerHistory.value.has(e.toLowerCase()))

            if (allowedTickers.value.length > 0) {
                try {
                    // starting ai report. updating loading store
                    
                    loading.startLoading();
                    const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/seven_p`, {
                        tickers: allowedTickers.value,
                        user_id:user_id,
                        report_type:"7_powers"
                    });
                    

                }
                catch (error) {
                    console.error('Error sending query', error);
                }
                finally {
                    loading.value = false;
                    tickers.value.forEach(t => tickerHistory.value.add(t.toLowerCase()));

                }
            }
        else{
                        messages.value.push({
                    text: "ticker analysis is empty or these tickers were already analysed in this session. analyse the ticker and then generate the 7 power report again or go to the main page and return to this page to get a new report",
                    isUser: false,
                    type: "error"
                })
        }
        }
        else {
            if (!rawMessage.value) {
                messages.value.push({
                    text: "analysis already done for this ticker, go back to the main page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
            }
            else {
                messages.value.push({
                    text: "analysis already done for this ticker, go back to the main page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
            }
        }
    }
}




</script>
<style>
h1 {
    text-align: center;
    font-size: 2em;
    margin-bottom: 20px;
    color: rgb(62, 61, 61);
}

h2 {
    text-align: center;
    font-size: 1em;
    margin-bottom: 20px;
    color: rgb(62, 61, 61);
}

.chat-messages {
    display: flex;
    flex-direction: column;
    width: 90%;
    max-width: 350px;
    padding: 10px;
    overflow-y: auto;
    border-radius: 8px;
    background-color: #000000c0;
    color: rgba(255, 255, 255, 0.66);
    line-height: 1.5;
    font-family: monospace;
    margin-bottom: 20px;
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

@media (max-width: 768px) {
    h1 {
        font-size: 1.5em;
    }

    button {
        width: 90%;
        padding: 12px;
    }

    .chat-messages {
        width: 100%;
    }
}

@media (min-width: 769px) {
    .page {
        padding: 50px;
    }

    .chat-messages {
        max-width: 800px;
    }

    button {
        width: auto;
        padding: 8px;
    }
}
</style>