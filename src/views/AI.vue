<template>
    <div>
        <div>
            <h1>7power Analysis Framework from Helmer Hamilton.</h1>
        </div>
        <div>
            <CompanyData />
        </div>

        <div class="chat-messages">
            <div v-for="(message, index) in messages" :key="index" :class="{ 'user-message': message.isUser }"
                v-html="message.text">
            </div>
        </div>
        <button @click="get_seven_p_analysis">7powers</button>
        <small> ⚠️warning it takes around 30 sec per ticker <br></small>

        <button @click="get7pPdf">get pdf</button>
        <div>
            <Navigation />
        </div>
        <div v-if="tickerHistory.size > 0">
            <small>
                <strong>ticker history:</strong> {{ [...tickerHistory].join(',') }}
            </small>
        </div>
        <div v-if="loading" class="loading-overlay">
            <div class="loading-throbber">
                <div class="spinner"></div>
                <p>Sending query...powered by google gemini flash please wait...</p>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref, watch } from 'vue';
import Navigation from '@/components/Navigation.vue';
import axios from 'axios';
import { useTickerStore } from '@/stores/tickerStore';
import CompanyData from './CompanyData.vue';
import { downloadPdfReport } from '@/utils/downloadReport';

const loading = ref(false);
const rawMessage = ref('');
const tickerHistory = ref(new Set())
const tickerStore = useTickerStore();
const allowedTickers = ref([]);
const tickers = ref([]);

const messages = ref([
    { text: 'I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start. ', isUser: false }
]);

async function get_seven_p_analysis() {
    tickers.value = tickerStore.currentTickers

    if (tickers.length === 0) {

        messages.value.push({
            text: 'ticker analysis is empty. there must be an analysis and 7powers analysis generated first',
            isUser: false
        })

    }
    else {
        if (tickers.value.length > 0) {

            allowedTickers.value = tickers.value.filter(e => !tickerHistory.value.has(e.toLowerCase()))

            if (allowedTickers.value.length > 0) {
                try {

                    loading.value = true
                    const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/seven_p`, {
                        tickers: allowedTickers.value
                    });
                    let formattedResponse = response.data['assistant'];
                    rawMessage.value = formattedResponse;
                    setTimeout(() => {

                        const jsonToTextResponse = formattedResponse.map(section => {
                            switch (section.type) {
                                case "title":
                                    return `<h2 class="text-xl font-bold mb-2">${section.content}</h2>`;
                                case "paragraph":
                                    return `<p class="text-base mb 3">${section.content}</p>`;
                                case "bullets":
                                    return `<ul class="mb-3">${section.content.map(e => `<li>${e}</li>`).join('').trim()}</ul>`
                                default:
                                    return '';
                            }
                        }
                        ).join('');

                        messages.value.push({ text: jsonToTextResponse, isUser: true });
                    }, 1000);

                }
                catch (error) {
                    console.error('Error sending query', error);
                }
                finally {
                    loading.value = false;
                    tickers.value.forEach(t => tickerHistory.value.add(t.toLowerCase()));

                }
            }
        else{
                        messages.value.push({
                    text: "ticker analysis is empty or these tickers were already analysed in this session. analyse the ticker and then generate the 7 power report again or go to the main page and return to this page to get a new report",
                    isUser: false,
                    type: "error"
                })
        }
        }
        else {
            if (!rawMessage.value) {
                messages.value.push({
                    text: "analysis already done for this ticker, go back to the main page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
            }
            else {
                messages.value.push({
                    text: "analysis already done for this ticker, go back to the main page and return to this section to get a new analysis",
                    isUser: false,
                    type: "error"
                })
            }
        }
    }
}
const get7pPdf = async () => {
    if (rawMessage.value.length > 0) {
        loading.value = true;
        try {
            await downloadPdfReport(rawMessage.value, tickerStore.currentTickers, "7powers")
        } catch (err) {
            console.error('error generating report ', err)
            messages.value.push({
                text: err,
                isUser: false
            })
        }
        finally {
            loading.value = false;
        }
    }
    else {
        messages.value.push({
            text: 'ticker analysis is empty. there must be an analysis and 7powers analysis generated first',
            isUser: false
        })
    }
}



</script>
<style scoped>
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