<template>
    <div style="position:fixed;top:10px;right:20px;">
        
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
                :disabled="loading.isLoading" 
                @click="get_report" 
                class="buttons">
            {{loading['isLoading'] ? 'generating report': 'GO'}}
            </button>
        </div>
    </div>
    <div class="error-message">
        {{ errorMessage }}
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
                <br></br>
                <div class="terminal">
                    all previous ai reports indexed: overall, seven powers, red flags. timestamped. your research trail
                    starts here.
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
import { ref, onMounted } from 'vue';
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
import { showTempMessage } from '@/utils/timeout';
import { formatDateAgo } from '@/utils/formateTime';
import { useSocket } from '@/composables/taskSocket';
import axios from 'axios';
import RedFlags from './RedFlags.vue';
import { fetch_reports, ai_reports } from '@/utils/fetch_reports';
import { useLoadingStore } from '@/stores/loadingStore';
const allowedTickers = ref([]);
const tickerHistory = ref(new Set());
const isConnected = useSocket();
const tickers = ref([]);
const errorMessage = ref('');
const tickerStore = useTickerStore();
const loading = useLoadingStore()
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

const get_report = async () => {
    const tickers = tickerStore.currentTickers;
    const user_id = localStorage.getItem('user_id')
    if (tickers.length == 0 || !user_id) {
        console.error('missing tickers');
        errorMessage.value = 'ticker or user_id is missing'
        showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 2000);
    }
    else {
        allowedTickers.value = tickers.filter(e => !tickerHistory.value.has(e.toLowerCase()))
        if (allowedTickers.value.length) {
            loading.startLoading();

            try {
                await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini`, {
                    tickers: allowedTickers.value,
                    user_id: user_id,
                    report_type: "overall-reports"
                })
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
            errorMessage.value = 'ticker previously analysed. refresh your browser if you need to analyse it again'
            showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 3000);
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
            errorMessage.value = 'no signed url available. try again later'
            showTempMessage(errorMessage, `(￣▽￣;)ゞ ${errorMessage.value}`, 2000);
            console.error('no signed url available. try again later')
        }
    }
    catch (err) {
        console.error("error: ", err)
    }

}
</script>
<style></style>
