<template>
    <div v-if="tickers.length>0">
        <div class="terminal">
            <span>eacsa> </span>trust and sentiment analysis with ai:
                                     <button 
                :disabled="isLoadingLocal||downloadingSecFiles||!isSocketReady" 
                @click="quant_rittenhouse" 
                class="buttons">
            {{isLoadingLocal ? 'generating report': 'GO'}}
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
      <div v-if="notification" :class="['msg', notification.type]">
        {{ notification.text}}
    </div>
    </div>
</template>

<script setup>
import { ref, computed,watch } from 'vue';
import Navigation from '@/components/Navigation.vue';
import axios from 'axios';
import { useTickerStore } from '@/stores/tickerStore';
import { useLoadingStore } from '@/stores/loadingStore';
import { showTempMessage } from '@/utils/showMessages';
import { useSocket } from '@/composables/taskSocket';
const isLoadingLocal = ref(false);
let localTaskID=null;
const rawMessage = ref('');
const tickerHistory = ref(new Set())
const tickerStore = useTickerStore();
const loading = useLoadingStore();
const isConnected = useSocket();
const allowedTickers = ref([]);
const final_report=ref('');
const notification = ref(null);
const downloadingSecFiles=ref(false);
const isSocketReady=ref(false);
const messages = ref([
    { text: 'I will conduct the a trust and sentiment analysis ofthe latest submitted reports. If you want analysis for another, ticker just change the ticker in the main page and pres analyze to start. ', isUser: false }
]);

watch(loading,()=>{
    if(localTaskID &&!loading.pendingTasks[localTaskID]){
        isLoadingLocal.value=false
        localTaskID=null;
        if(loading.lastStatus=="done")
        {
            showTempMessage(notification,"report completed. go to the s3 report section","notification",5000);
        }
        else if(loading.lastStatus=="error")
        {
            showTempMessage(notification,"error trying to generate the pdf. refresh the browser and try again","error",5000);
            const last = tickers.value.at(-1)
            tickerHistory.value.delete(last)
            tickerHistory.value = new Set(tickerHistory.value)
        }
    }
})
watch (loading,()=>{
    if(tickers.value.length>0){
    downloadingSecFiles.value=loading.isLoading
    }
})

watch(isConnected.isConnected,()=>{
    isSocketReady.value=isConnected.socket.connected

})

const tickers= computed(()=> tickerStore.currentTickers);
async function quant_rittenhouse() {
    
    const user_id = localStorage.getItem('user_id')
    if (tickers.value.length === 0 || !user_id) {
        
        messages.value.push({
            text: 'ticker analysis or user_id empty',
            isUser: false
        })
        
        showTempMessage(notification, "ticker analysis is empty","error")

    }
    else {
        if (tickers.value.length > 0) {
            allowedTickers.value = tickers.value.filter(e => !tickerHistory.value.has(e.toLowerCase()))

            if (allowedTickers.value.length > 0) {
                try {
                    // starting ai report. updating loading store

                    isLoadingLocal.value=true;
                    const response=await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/analyze_rittenhouse`, {
                        tickers: allowedTickers.value,
                        user_id: user_id,
                        report_type: "eacsa-rittenhouse"
                    });
                    localTaskID=response.data.task_id;
                    loading.addTask[localTaskID]
                }
                catch (error) {
                    console.error('Error sending query', error);
                    isLoadingLocal.value=false;
                    tickerHistory.value.pop()

                    
                    showTempMessage(notification,"Error sending query","error")
                }
                finally {
                    
                    tickers.value.forEach(t => tickerHistory.value.add(t.toLowerCase()));

                }
            }
            else {
                messages.value.push({
                    text: "ticker analysis is empty or these tickers were already analysed in this session. analyse the ticker and then generate the  report again or go to the main page and return to this page to get a new report",
                    isUser: false,
                    type: "error"
                })
                showTempMessage(notification,"ticker analysis is empty or these tickers were already analysed in this session. analyse the ticker and then generate report again or go to the main page and return to this page to get a new report","error",10000)
            }
        }
        else {
            if (!rawMessage.value) {
                messages.value.push({
                    text: "analysis already done for this ticker, refresh the page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
                
                showTempMessage(notification,"analysis already done for this ticker, refresh the page and return to this section to get a new analysis","error",10000)
            }
            else {
                messages.value.push({
                    text: "analysis already done for this ticker, refresh the page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
                
                showTempMessage(notification,"analysis already done for this ticker, refresh the page and return to this section to get a new analysis","error",10000)
            }
        }
    }
}




</script>
<style>

</style>