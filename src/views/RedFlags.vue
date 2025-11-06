<template>
    <div>
        <div>
            <h1 class="app-title">Red Flags.</h1>
        </div>
        <button :disabled="tickers.length === 0" @click="red_flag_analysis">
            Red Flags
        </button>
        <div>
            <Navigation />
        </div>
        <div v-if="tickerHistory.size > 0">
            <small>
                <strong>ticker history:</strong> {{ [...tickerHistory].join(',') }}
            </small>
        </div>
        <div>
            {{ final_report['final_report'] }}
        </div>
        <div class="error-message">
            {{ errorMessage }}
        </div>
    </div>

</template>

<script setup>
import { ref, computed } from 'vue';
import Navigation from '@/components/Navigation.vue';
import axios from 'axios';
import { useTickerStore } from '@/stores/tickerStore';
import { useLoadingStore } from '@/stores/loadingStore';
import { showTempMessage } from '@/utils/timeout';

const rawMessage = ref('');
const tickerHistory = ref(new Set())
const tickerStore = useTickerStore();
const loading = useLoadingStore();
const allowedTickers = ref([]);
const final_report=ref('');
const errorMessage = ref('');
const messages = ref([
    { text: 'I will conduct the report analysis and identify red flags. If you want analysis for another, ticker just change the ticker in the main page and pres analyze to start. ', isUser: false }
]);

const tickers= computed(()=> tickerStore.currentTickers);
async function red_flag_analysis() {
    
    const user_id = localStorage.getItem('user_id')
    console.log(tickers)
    if (tickers.value.length === 0 || !user_id) {
        
        messages.value.push({
            text: 'ticker analysis or user_id empty',
            isUser: false
        })
        errorMessage.value = 'ticker analysis is empty. there must be an analysis and 7powers analysis generated first'
        showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 2000);

    }
    else {
        if (tickers.value.length > 0) {

            allowedTickers.value = tickers.value.filter(e => !tickerHistory.value.has(e.toLowerCase()))

            if (allowedTickers.value.length > 0) {
                try {
                    // starting ai report. updating loading store

                    loading.startLoading();
                    const response =  await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/quant`, {
                        tickers: allowedTickers.value,
                        user_id: user_id,
                        report_type: "red-flags"
                    });

                    final_report.value=response.data['final_report']



                }
                catch (error) {
                    console.error('Error sending query', error);

                    errorMessage.value = 'Error sending query'
                    showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 2000);
                }
                finally {
                    loading.stopLoading()
                    tickers.value.forEach(t => tickerHistory.value.add(t.toLowerCase()));

                }
            }
            else {
                messages.value.push({
                    text: "ticker analysis is empty or these tickers were already analysed in this session. analyse the ticker and then generate the red flag report again or go to the main page and return to this page to get a new report",
                    isUser: false,
                    type: "error"
                })
                errorMessage.value = 'ticker analysis is empty or these tickers were already analysed in this session. analyse the ticker and then generate the red flag report again or go to the main page and return to this page to get a new report'
                showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 3000);
            }
        }
        else {
            if (!rawMessage.value) {
                messages.value.push({
                    text: "analysis already done for this ticker, refresh the page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
                errorMessage.value = 'analysis already done for this ticker, refresh the page and return to this section to get a new analysis'
                showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 3000);
            }
            else {
                messages.value.push({
                    text: "analysis already done for this ticker, refresh the page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
                errorMessage.value = 'analysis already done for this ticker, refresh the page and return to this section to get a new analysis'
                showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 3000);
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