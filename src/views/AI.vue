<template>
    <div>
        <div>
            <h1>7power Analysis Framework from Helmer Hamilton.</h1>
        </div>
        <div>
            <CompanyData/>
        </div>

        <div class="chat-messages">
            <div v-for="(message, index) in messages" :key="index" :class="{ 'user-message': message.isUser }"
                v-html="message.text">
            </div>
        </div>
        <button @click="sendMessage">7powers</button>
        <button @click="get7pPdf">get pdf</button>
        <div>
            <Navigation/>
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
const loading = ref(false);
const userMessage = ref('');

const tickerStore=useTickerStore();



const messages = ref([
    { text: 'I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start. ', isUser: false }
]);

async function sendMessage() {
    const tickers =tickerStore.currentTickers
    
    if ( tickers.length>0) {
        try {

            loading.value = true 
            const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/chat`, {
                query: tickers
            });
    
            setTimeout(() => {
                let formattedResponse = response.data['assistant']
                    // .replace(/\* \*\*/g, '<br>')
                    // .replace(/\. \*\*/g, '<br>')
                    // .replace(/\:\*\*/g, '<br><br>')
                    // .replace(/\*\*/g, '<br><br>');
                    .replace(/\n/g, '<br>');

                formattedResponse = formattedResponse.trim(); // Remove any leading new line or space
                messages.value.push({ text: formattedResponse, isUser: true });
            }, 1000);

        }
        catch (error) {
            console.error('Error sending query', error);
        } loading.value = false;
    }
    else {
        console.error('no tickers found. add a ticker in the ticker field and hit analyse and then you will be able to use 7powers and pdf report buttons')
        messages.value.push({
        text: "no tickers found. add a ticker in the ticker field and hit analyse and then you will be able to use 7powers and pdf report buttons",
        isUser: false
    })}
}
const get7pPdf= async ()=>{
    const finalReport=messages.value.filter(e=>e['isUser']===true)
    if(finalReport.length>0){
        const jsonMatch =finalReport[0].text.match(/```json\s*([\s\S]*?)```/)
        loading.value=true; 
        try{
            const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini/report`,{
                ai_report:jsonMatch[1].replace(/<br>/g,'')
            },
            {
                responseType:'blob'
            })
            const blob = new Blob([response.data],{
                type:'application/pdf'
            })
            
            const objectUrl= URL.createObjectURL(blob)
            const link=document.createElement('a')
            link.href=objectUrl
            link.download=`${response.data.size}_${tickerStore.currentTickers.join('_')}.pdf`||'7_powers.pdf'
            document.body.appendChild(link)
            link.click()
            URL.revokeObjectURL(objectUrl)
            document.body.removeChild(link)
        }catch(err){
            console.error('error generating report ',err)
            messages.value.push({
                text:err,
                isUser:false
            })
        }
        finally{
            loading.value=false;
        }
    }
    else{
        console.error('there is no analysis. please execute the analyisis to get a report')
        messages.value.push({
            text:'there is no analysis. please execute the analyisis to get a report',
            isUser:false
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