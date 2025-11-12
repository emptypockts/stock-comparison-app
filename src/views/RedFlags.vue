<template>
    <div v-if="tickers.length>0">
        <div class="terminal">
            <span>eacsa> </span>red flag report with ai:
        
                                     <button 
                :disabled="loading.isLoading" 
                @click="red_flag_analysis" 
                class="buttons">
            {{loading['isLoading'] ? 'generating report': 'GO'}}
            </button>
        </div>
        <div>
            <Navigation />
        </div>
        <div class="console-report" v-if="final_report.length">
            
            <template v-for="(item,index) in final_report" :key="index">
                <div v-if="item.type==='title'" class="console-title">
                    {{ item.content }}
                </div>
                <div v-else-if="item.type==='paragraph'" class="console-paragraph">
                    {{ item.content }}
                </div>
                <ul v-else-if="item.type==='bullets'" class="console-bullets">
                    <li v-for="(b,i) in item.content" :key="i">
                        {{ b }}
                    </li>
                </ul>

            </template>
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
                    await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/quant`, {
                        tickers: allowedTickers.value,
                        user_id: user_id,
                        report_type: "eacsa-red-flags"
                    });
                    
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

</style>