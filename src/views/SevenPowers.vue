<template>
    <div v-if="tickers.length>0">
        
        <div class="terminal">
        <span>eacsa> </span>seven powers report with ai:
            
                             <button 
                :disabled="isLoadingLocal||!isSocketReady" 
                @click="get_seven_p_analysis" 
                class="buttons">
            {{isLoadingLocal ? 'generating report': 'GO'}}
            </button>
        </div>
        <div>
            <Navigation />
        </div>
      <div v-if="notification" :class="['msg', notification.type]">
        {{ notification.text}}
    </div>
    </div>

</template>

<script setup>
import { ref, computed, watch } from 'vue';
import Navigation from '@/components/Navigation.vue';
import axios from 'axios';
import { useTickerStore } from '@/stores/tickerStore';
import { useLoadingStore } from '@/stores/loadingStore';
import { showTempMessage } from '@/utils/showMessages';
import { useSocket } from '@/composables/taskSocket';

const rawMessage = ref('');
const tickerHistory = ref(new Set())
const tickerStore = useTickerStore();
const loading = useLoadingStore();
const allowedTickers = ref([]);
const notification = ref(null);
const isLoadingLocal=ref(false);
const isConnected = useSocket();
const isSocketReady=ref(false);
let localTaskID=null;
const messages = ref([
    { text: 'I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start. ', isUser: false }
]);
watch(loading,()=>{
    if(localTaskID &&!loading.pendingTasks[localTaskID]){
        isLoadingLocal.value=false
        localTaskID=null;
        if(loading.lastStatus=="done")
        {
            showTempMessage(notification,"report completed. go to the s3 report section","notification",20000);
        }
        else if(loading.lastStatus=="error")
        {
            showTempMessage(notification,"error trying to generate the pdf. refresh the browser and try again","error",20000);
        }
    }
})
watch(isConnected.isConnected,()=>{
    isSocketReady.value=isConnected.socket.connected

})
const tickers =computed(()=> tickerStore.currentTickers)
async function get_seven_p_analysis() {
    
    const user_id = localStorage.getItem('user_id')
    if (tickers.value.length === 0 || !user_id) {
        
        messages.value.push({
            text: 'ticker analysis or user_id empty',
            isUser: false
        })
        
        showTempMessage(notification, "ticker analysis is empty. there must be an analysis and 7powers analysis generated first","error")

    }
    else {
        if (tickers.value.length > 0) {

            allowedTickers.value = tickers.value.filter(e => !tickerHistory.value.has(e.toLowerCase()))

            if (allowedTickers.value.length > 0) {
                try {
                    // starting ai report. updating loading store

                    isLoadingLocal.value=true;
                    const  response= await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/seven_p`, {
                        tickers: allowedTickers.value,
                        user_id: user_id,
                        report_type: "seven-powers"
                    });
                    localTaskID=response.data.task_id
                    loading.addTask(localTaskID)
                }
                catch (error) {
                    console.error('Error sending query', error);
                    isLoadingLocal.value=false;
                    
                    showTempMessage(notification,"error sending query","error")
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
            
            showTempMessage(notification,"ticker previously analysed. refresh your browser if you need to analyse it again","error")
            }
        }
        else {
            if (!rawMessage.value) {
                messages.value.push({
                    text: "ticker previously analysed. refresh your browser if you need to analyse it again",
                    isUser: false,
                    type: "error"
                })
                
                showTempMessage(notification,"ticker previously analysed. refresh your browser if you need to analyse it again","error")
            }
            else {
                messages.value.push({
                    text: "ticker previously analysed. refresh your browser if you need to analyse it again",
                    isUser: false,
                    type: "error"
                })
                
                showTempMessage(notification,"ticker previously analysed. refresh your browser if you need to analyse it again","error")
            }
        }
    }
}




</script>
<style>

</style>