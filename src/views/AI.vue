<template>
    <div v-if="tickers.length>0">
        <div class="terminal">
        <span>eacsa> </span>seven powers report with ai:
        <button  @click="get_seven_p_analysis" class="buttons">
            ↲
        </button>
        </div>
        <div>
            <Navigation />
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
const errorMessage = ref('');
const messages = ref([
    { text: 'I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start. ', isUser: false }
]);
const tickers =computed(()=> tickerStore.currentTickers)
async function get_seven_p_analysis() {
    
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
                     await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/seven_p`, {
                        tickers: allowedTickers.value,
                        user_id: user_id,
                        report_type: "seven-powers"
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
                    text: "ticker previously analysed. refresh your browser if you need to analyse it again",
                    isUser: false,
                    type: "error"
                })
            errorMessage.value = 'ticker previously analysed. refresh your browser if you need to analyse it again'
            showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 3000);
            }
        }
        else {
            if (!rawMessage.value) {
                messages.value.push({
                    text: "ticker previously analysed. refresh your browser if you need to analyse it again",
                    isUser: false,
                    type: "error"
                })
                errorMessage.value = 'ticker previously analysed. refresh your browser if you need to analyse it again'
                showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 3000);
            }
            else {
                messages.value.push({
                    text: "ticker previously analysed. refresh your browser if you need to analyse it again",
                    isUser: false,
                    type: "error"
                })
                errorMessage.value = 'ticker previously analysed. refresh your browser if you need to analyse it again'
                showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 3000);
            }
        }
    }
}




</script>
<style>

</style>