<template>
    <div style="position:fixed;top:10px;right:40px;">
        
        <p v-if="isConnected" style="color:greenyellow;font-size: 14px;border: greenyellow double 1px;padding: 10px;">AI on</p>
        <p  v-else style="color:red;font-size: 14px;border: red double 1px;padding: 10px;">AI off</p>
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
                :disabled="isLoadingLocal" 
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
        <AI :tickers="tickers" />
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
import { ref, onMounted, watch } from 'vue';
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
import { showTempMessage } from '@/utils/showMessages';
import { formatDateAgo } from '@/utils/formateTime';
import { useSocket } from '@/composables/taskSocket';
import axios from 'axios';
import RedFlags from './RedFlags.vue';
import { fetch_reports, ai_reports } from '@/utils/fetch_reports';
import { useLoadingStore } from '@/stores/loadingStore';
import { data } from 'jquery';
const allowedTickers = ref([]);
const tickerHistory = ref(new Set());
const isConnected = useSocket();
const tickers = ref([]);
const notification = ref(null);
const tickerStore = useTickerStore();
const loading = useLoadingStore()
const isLoadingLocal=ref(false)
let localTaskID=null;
const updateTickers = (newTickers) => {
    tickerStore.updateTickers(newTickers)
    tickers.value = tickerStore.currentTickers
}
const collapsed = ref(true)
const toggleCollapse = () => {
    collapsed.value = !collapsed.value;
};


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
