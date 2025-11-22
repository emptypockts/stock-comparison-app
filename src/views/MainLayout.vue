<template>
    <div id="aiStatusBox" @click="toggleToolTip"
    style="position:fixed;top:10px;right:40px; display: flex;align-items: center;gap: 10px;">
        <p 
        :style="{
            color: isSocketReady ? 'greenyellow': 'red',
            border: isSocketReady ? '1px double greenyellow' : '1px double red',
            fontSize:'14px',
            padding:'10px'
            }">
            {{ isSocketReady ? 'AI on':'AI off' }}
         </p>
            <span
            v-if="notifStore.unreadCount()>0"
            style="position: absolute;top: 8px;right: -8px;background: red;color: white;border-radius: 50%;padding: 3px 7px;font-size: 7px;border: 2px solid white;"
            >
            {{ notifStore.unreadCount() }}
        </span>
        <div class="tooltip" :class="{show :showTooltip}">
        <div v-if="showTooltip&&notifStore.list.length>0"
            style="position: absolute;
            top: 40px;
            right: 70px;
            background: blue;
            color: white;
            padding: 10px;
            border: solid 1px greenyellow;
            border-radius: 4px;
            width: 200px;
            z-index: 999;"
            
            >
            <p style="font-weight: bold;margin-bottom: 5px;">Reports Ready</p>
            <div v-for="note in notifStore.list" :key="note.id"
            style="margin-bottom: 8px;display: flex;justify-content: space-between;align-items: center;"
            >
            <a h:ref="note.url" 
            class="notif-link"
            @click="notifStore.markRead(note.task_id);download_s3_report(note.report_type, note.task_id)"
            >
                {{note.report_type}}-{{ note.tickers[0] }}
            </a>
            </div>
        </div>

        </div>
        </div>
    <div>
        
        <CompanyData @tickers-updated="updateTickers" />
        <ValueStockAnalysis :tickers="tickers" />
    </div>

    <div>
        
        <StockFinancialCharts :tickers="tickers" />
    </div>
    <div>
        <IntrinsicValue :tickers="tickers" />
    </div>
    <div v-if="tickers.length > 0">
        <div class="terminal">
            <span>eacsa> </span>financial report with ai:
                                    <button 
                :disabled="(isLoadingLocal||!isSocketReady)" 
                @click="get_report" 
                class="buttons">
            {{isLoadingLocal ? 'generating report': 'GO'}}
            </button>
        </div>
    </div>
      <div v-if="notification" :class="['msg', notification.type]">
        {{ notification.text}}
    </div>
    <div>
        <RittenhouseAnalysis :tickers="tickers" />
    </div>
    <div>
        <SevenPowers :tickers="tickers" />
    </div>
    <div>
        <RedFlags :tickers="tickers" />
        <div class="terminal">
            <span>eacsa> </span>query S3 archives:
        </div>
        <button @click="toggleCollapse" class="buttons">
            ⟬⟬ expand/collapse ⟭⟭
        </button>

        <div v-if="!collapsed" class="table-container">
            <div v-if="ai_reports">
                
                <div class="terminal">
                    <p>
                    all previous ai reports indexed: overall, seven powers, red flags. timestamped. your research trail starts here.
                    </p>
                </div>
                <table>
                    <thead>
                        <tr>
                            <th>report type</th>
                            <th>ticker</th>
                            <th>timestamp</th>
                            <th>download</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(k, v) in ai_reports" :key="k">
                            <td> {{ k['report_type'] }}</td>
                            <td> {{ k['tickers'][0] }}</td>
                            <td> {{ formatDateAgo(k['timestamp']) }} ago</td>

                            <td>
                                <a href="#" @click.prevent="download_s3_report(k['report_type'], k['task_id'])"
                                    class="download-link">
                                    download
                                </a>
                            </td>
                        </tr>
                    </tbody>
                </table>
            </div>

            <div v-else>
                <strong>
                    no reports found
                </strong>
            </div>
        </div>
    </div>
    <div>
        <Navigation />
        <CookieBanner />
        <LoginAlert />
    </div>
    
</template>
<script setup>
import { ref, onMounted, watch ,onBeforeMount} from 'vue';
import IntrinsicValue from '@/views/IntrinsicValue.vue';
import CompanyData from '@/views/CompanyData.vue';
import StockFinancialCharts from '@/views/StockFinancialCharts.vue';
import ValueStockAnalysis from '@/views/ValueStockAnalysis.vue';
import RittenhouseAnalysis from "@/views/RittenhouseAnalysis.vue";
import SevenPowers from "@/views/SevenPowers.vue"
import { useTickerStore } from '@/stores/tickerStore';
import Navigation from '@/components/Navigation.vue';
import CookieBanner from '@/components/CookieBanner.vue';
import LoginAlert from '@/components/LoginAlert.vue';
import { showTempMessage } from '@/utils/showMessages';
import { formatDateAgo } from '@/utils/formateTime';
import { useSocket } from '@/composables/taskSocket';
import axios from 'axios';
import RedFlags from './RedFlags.vue';
import { fetch_reports, ai_reports } from '@/utils/fetch_reports';
import { useLoadingStore } from '@/stores/loadingStore';
import { useNotificationStore } from '@/stores/notificationStore';

const showTooltip =ref(false);
const notifStore=useNotificationStore();
const allowedTickers = ref([]);
const tickerHistory = ref(new Set());
const isConnected = useSocket();
const tickers = ref([]);
const notification = ref(null);
const tickerStore = useTickerStore();
const loading = useLoadingStore()
const isLoadingLocal=ref(false)
const isSocketReady=ref(false);
let localTaskID=null;
const updateTickers = (newTickers) => {
    tickerStore.updateTickers(newTickers)
    tickers.value = tickerStore.currentTickers
}
const collapsed = ref(true)

const toggleCollapse = () => {
    collapsed.value = !collapsed.value;
};
let tooltipTimer=null;

function toggleToolTip(){
    
       showTooltip.value=!showTooltip.value
    
}
function hideToolTip(){
    showTooltip.value=false
}

onMounted(async () => {
    ai_reports.value = await fetch_reports();
})

watch(loading.pendingTasks,()=>{
    if(localTaskID &&!loading.pendingTasks[localTaskID]){
        isLoadingLocal.value=false
        localTaskID=null;
        showTempMessage(notification,"report completed. go to the s3 report section","notification",20000);
    }
})
watch(isConnected.isConnected,()=>{
    isSocketReady.value=isConnected.socket.connected

})

function handleClickOutside(event){
    const el=document.querySelector('#aiStatusBox')
    if (el &&!el.contains(event.target)){
        showTooltip.value=false
    }

}
onMounted(()=>document.addEventListener('click',handleClickOutside));
onBeforeMount(()=>document.addEventListener('click',handleClickOutside))

const get_report = async () => {
    const tickers = tickerStore.currentTickers;
    const user_id = localStorage.getItem('user_id')
    if (tickers.length == 0 || !user_id) {
        console.error('missing tickers');
        
        showTempMessage(notification, "ticker or user_id is missing","error");
    }
    else {
        allowedTickers.value = tickers.filter(e => !tickerHistory.value.has(e.toLowerCase()))
        if (allowedTickers.value.length) {
            isLoadingLocal.value=true

            try {
               const response= await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini`, {
                    tickers: allowedTickers.value,
                    user_id: user_id,
                    report_type: "overall-reports"
                })
                localTaskID=response.data.task_id
                loading.addTask(localTaskID)
            }
            
            catch (err) {
                console.error('error trying to generate report:', err)
            }
            finally {
                tickers.forEach(t => tickerHistory.value.add(t.toLowerCase()))
                ai_reports.value = await fetch_reports();
            }
        }
        else {
            
            showTempMessage(notification, "ticker previously analysed. refresh your browser if you need to analyse it again","error");
        }
    }
}


async function download_s3_report(bucket_name, file_name) {
    try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/v1/user_report`, {
            params:
            {
                bucket_name: bucket_name,
                file_name: file_name,
                client_method: "get_object"
            }

        });

        const signed_url = response.data.signed_url
        if (signed_url) {
            window.open(signed_url, '_blank')
        }
        else {
            
            showTempMessage(notification, "no signed url available. try again later","error");
            console.error('no signed url available. try again later')
        }
    }
    catch (err) {
        console.error("error: ", err)
    }

}
</script>
<style></style>
