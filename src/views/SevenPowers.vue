<template>
        
    <div v-if="tickers.length>0">        
        <div class="terminal">
        <span>eacsa> </span>seven powers report with ai:
                             <button 
                :disabled="(isLoadingLocal||!haveCredits)"
                @click="get_seven_p_analysis" 
                class="buttons">
              {{ isLoadingLocal||!haveCredits ? 'DISABLED' : 'GO' }}
            </button>            
        
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
import { pollTaskStatus } from '@/utils/pollTask';
import { fetch_reports, ai_reports } from '@/utils/fetch_reports';
import { validateCredits } from '@/utils/credits';
import { useNotificationStore } from '@/stores/notificationStore';
const notifStore = useNotificationStore();

// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// import { useSocket } from '@/composables/taskSocket';
const isLoadingLocal=ref(false);
const haveCredits = ref(true);
const usedCredits= ref(0);
const rawMessage = ref('');
const tickerHistory = ref(new Set())
const tickerStore = useTickerStore();
const loading = useLoadingStore();
const allowedTickers = ref([]);
const notification = ref(null);
// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// const isConnected = useSocket();
// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// const isSocketReady=ref(false);
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
watch(notifStore.list, ()=>{
    usedCredits.value=[...new Set(notifStore.list.flatMap(t => t.tickers))].length
    haveCredits.value =  validateCredits(usedCredits.value)
})
// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// watch(isConnected.isConnected,()=>{
//     isSocketReady.value=isConnected.socket.connected
// })
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
                    loading.startLoading()
                    isLoadingLocal.value=true;
                    const  response= await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/seven_p`, {
                        tickers: allowedTickers.value,
                        user_id: user_id,
                        report_type: "seven-powers"
                    });
                    localTaskID=response.data.task_id
                    loading.addTask(localTaskID)
                    tickers.value.forEach(t => tickerHistory.value.add(t.toLowerCase()));
                    pollTaskStatus({
                    task_id: localTaskID,
                    user_id,
                    msInterval: 5000,
                    maxAttempts: 120,
                    onOngoing: data => {
                        console.log("taks is still running: ", data[0].status)
                    },
                    onCompleted: async data => {
                        console.log("task completed", data)
                        try {
                            ai_reports.value = await fetch_reports();
                        } catch (err) {
                            console.error("error fetching reports after task completion", err)
                            showTempMessage(notification,"error fetching reports after task completion","error")
                        }
                        
                        finally{
                        
                        isLoadingLocal.value = false
                        notifStore.add({
                        task_id: localTaskID,
                        tickers: allowedTickers.value,
                        report_type: response.data.report_type
                        
                    })
                        loading.stopLoading()
                        loading.completeTask(localTaskID)
                        }
                    },
                    onFailed: data => {
                        console.error("task failed: ", data)
                        showTempMessage(notification, "ai report generation failed. ", "error",10000);
                        isLoadingLocal.value = false
                    },
                    onTimeout: data=>{
                        console.error("polling timeout: ",data)
                        showTempMessage(notification,"report taking longer than expected. please check again later and refresh your browser","error")
                        isLoadingLocal.value=false
                    }
                })
                }
                catch (error) {
                    console.error('Error sending query', error);
                    isLoadingLocal.value=false;
                    
                    showTempMessage(notification,"error sending query","error")
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