<template>
    {{ validateCredits(usedCredits) }}
    <div id="aiStatusBox" @click="toggleToolTip"
        style="position:fixed;top:10px;right:30px; display: flex;align-items: center;gap: 10px;">
        <p :style="{
            color: haveCredits ? 'greenyellow' : 'red',
            border: haveCredits ? '1px double greenyellow' : '1px double red',
            fontSize: '14px',
            padding: '10px'
        }">
            credits: {{ 3 - usedCredits}} of 3

        </p>
        <span v-if="notifStore.unreadCount() > 0"
            style="position: absolute;top: 8px;right: -8px;background: red;color: white;border-radius: 50%;padding: 3px 7px;font-size: 7px;border: 2px solid white;">
            {{ notifStore.unreadCount() }}
        </span>
        <div class="tooltip" :class="{ show: showTooltip }">
            <div v-if="showTooltip && notifStore.list.length > 0" style="position: absolute;
            top: 40px;
            right: 70px;
            background: blue;
            color: white;
            padding: 10px;
            border: solid 1px greenyellow;
            border-radius: 4px;
            width: 200px;
            z-index: 999;">
                <p style="font-weight: bold;margin-bottom: 5px;">Reports Ready</p>
                <div v-for="note in notifStore.list" :key="note.id"
                    style="margin-bottom: 8px;display: flex;justify-content: space-between;align-items: center;">
                    <a h:ref="note.url" class="notif-link"
                        @click="notifStore.markRead(note.task_id); download_s3_report(note.report_type, note.task_id)">
                        {{ note.report_type }}-{{ note.tickers[0] }}
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

            <button :disabled="(isLoadingLocal || !haveCredits)" @click="get_report" class="buttons">
                {{ isLoadingLocal || !haveCredits ? 'DISABLED' : 'GO' }}

            </button>
        </div>
    </div>
    <div v-if="notification" :class="['msg', notification.type]">
        {{ notification.text }}
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
                        all previous ai reports indexed: overall, seven powers, red flags. timestamped. your research
                        trail starts here.
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
import { ref, onMounted, watch, onUnmounted, computed } from 'vue';
import { pollTaskStatus } from '@/utils/pollTask'
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
import { validateCredits } from '@/utils/credits';
// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// import { useSocket } from '@/composables/taskSocket';

import axios from 'axios';
import RedFlags from './RedFlags.vue';
import { fetch_reports, ai_reports } from '@/utils/fetch_reports';
import { useLoadingStore } from '@/stores/loadingStore';
import { useNotificationStore } from '@/stores/notificationStore';

const showTooltip = ref(false);
const notifStore = useNotificationStore();
const allowedTickers = ref([]);
const tickerHistory = ref(new Set());
const haveCredits = ref(true);
const usedCredits = ref(0)
// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// const isConnected = useSocket();

const tickers = ref([]);
const notification = ref(null);
const tickerStore = useTickerStore();
const loading = useLoadingStore()
const isLoadingLocal = ref(false);
// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
// const isSocketReady=ref(false);

let localTaskID = null;
const updateTickers = (newTickers) => {
    tickerStore.updateTickers(newTickers)
    tickers.value = tickerStore.currentTickers
}
tickers.value = computed(() => tickerStore.currentTickers);

const collapsed = ref(true)

const toggleCollapse = () => {
    collapsed.value = !collapsed.value;
};
let tooltipTimer = null;

function toggleToolTip() {

    showTooltip.value = !showTooltip.value

}
function hideToolTip() {
    showTooltip.value = false
}

onMounted(async () => {
    ai_reports.value = await fetch_reports();
    // this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.
    // isSocketReady.value=isConnected.socket.connected
})

watch(loading, () => {
    if (localTaskID && !loading.pendingTasks[localTaskID]) {
        isLoadingLocal.value = false
        localTaskID = null;
        if (loading.lastStatus == "done") {
            showTempMessage(notification, "report completed. Report sent to your email linked to this account. Also you can find the report on the s3 report section", "notification", 5000);
        }
        else if (loading.lastStatus == "error") {
            showTempMessage(notification, "error trying to generate the pdf. refresh the browser and try again", "error", 5000);
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

function handleClickOutside(event) {
    const el = document.querySelector('#aiStatusBox')
    if (el && !el.contains(event.target)) {
        showTooltip.value = false
    }

}
onMounted(() => document.addEventListener('click', handleClickOutside));
onUnmounted(() => { document.removeEventListener('click', handleClickOutside) })
const get_report = async () => {
    const tickers = tickerStore.currentTickers;
    const user_id = localStorage.getItem('user_id')
    if (tickers.length == 0 || !user_id) {
        console.error('missing tickers');

        showTempMessage(notification, "ticker or user_id is missing", "error");
    }
    else {
        allowedTickers.value = tickers.filter(e => !tickerHistory.value.has(e.toLowerCase()))
        if (allowedTickers.value.length) {
            loading.startLoading()
            isLoadingLocal.value = true

            try {
                const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini`, {
                    tickers: allowedTickers.value,
                    user_id: user_id,
                    report_type: "overall-reports"
                })
                localTaskID = response.data.task_id
                loading.addTask(localTaskID)
                tickers.forEach(t => tickerHistory.value.add(t.toLowerCase()))

                pollTaskStatus({
                    task_id: localTaskID,
                    user_id,
                    msInterval: 5000,
                    maxAttempts: 120,
                    onOngoing: data => {
                    },
                    onCompleted: async data => {
                        console.log("task completed", data)
                        try {
                            ai_reports.value = await fetch_reports();

                        } catch (err) {
                            console.error("error fetching reports after task completion", err)
                            showTempMessage(notification, "error fetching reports after task completion", "error")
                        }

                        finally {

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
                        showTempMessage(notification, "ai report generation failed. ", "error", 10000);
                        isLoadingLocal.value = false
                    },
                    onTimeout: data => {
                        console.error("polling timeout: ", data)
                        showTempMessage(notification, "report taking longer than expected. please check again later and refresh your browser", "error")
                        isLoadingLocal.value = false
                    }
                })
            }
            catch (err) {
                console.error('error calling ai gemini api:', err)
                isLoadingLocal.value = false
            }
        }
        else {

            showTempMessage(notification, "ticker previously analysed. refresh your browser if you need to analyse it again", "error");
            isLoadingLocal.value = false
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

            showTempMessage(notification, "no signed url available. try again later", "error");
            console.error('no signed url available. try again later')
        }
    }
    catch (err) {
        console.error("error: ", err)
    }

}
</script>
<style></style>
