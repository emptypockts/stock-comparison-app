<template>
    <div>
        <div>
            <h1>7power Analysis Framework from Helmer Hamilton.</h1>
        </div>

        <div class="chat-messages">
            <div v-for="(message, index) in messages" :key="index" :class="{ 'user-message': message.isUser }"
                v-html="message.text">
            </div>
        </div>

        <!-- <textarea v-model="userMessage" @keyup.enter="sendMessage" placeholder="Type a message..." rows="2"
                class="chatty-textarea" disabled>
                </textarea> -->
        <button @click="sendMessage">Send</button>

        <div>
            <Navigation/>
        </div>
        <div v-if="loading" class="loading-overlay">
            <div class="loading-throbber">
                <div class="spinner"></div>
                <p>Sending query...Powered by google Gemini 1.5 flash Please wait...</p>
            </div>
        </div>
    </div>

</template>

<script setup>
import { ref, watch } from 'vue';
import Navigation from '@/components/Navigation.vue';
// import { useRouter } from 'vue-router';
import axios from 'axios';
const analysisDone = ref(false);
const loading = ref(false);
const userMessage = ref('');
const ticker = ref('')



// const router = useRouter();
const messages = ref([
    { text: 'I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start. ', isUser: false }
]);

async function sendMessage() {
    ticker.value = localStorage.getItem('ticker')
    userMessage.value = `You are a financial expert that will conduct the 7power analysis framework from Hamilton Helmer about the company with ticker ${ticker.value}. Layout each of the 7 powers and your conclusion of each. Include any URL for reference.Make the analysis with the latest information and display those dates for any reference.
    You must include the urls used for this research.`;
    if (userMessage.value.trim() && !analysisDone.value && ticker.value) {
        messages.value.push({ text: userMessage.value, isUser: true });
        try {

            console.log("Sending query")
            console.log("loading status:", loading)
            loading.value = true // Loading state for authentication
            const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/chat`, {
                query: userMessage.value,
            });
            setTimeout(() => {
                let formattedResponse = response.data['assistant']
                    // .replace(/\* \*\*/g, '<br>')
                    // .replace(/\. \*\*/g, '<br>')
                    // .replace(/\:\*\*/g, '<br><br>')
                    // .replace(/\*\*/g, '<br><br>');
                    .replace(/\n/g, '<br>');

                formattedResponse = formattedResponse.trim(); // Remove any leading new line or space
                messages.value.push({ text: formattedResponse, isUser: false });
                localStorage.removeItem('ticker')
                analysisDone.value = true;
            }, 1000);

        }
        catch (error) {
            console.error('Error sending query', error);
        } loading.value = false;
    }
    else (messages.value.push({
        text: "<br>This ticker has been analysed already or the ticker field is empty. If you don't see any analysis done yet, try to update the ticker field and click the analyse button and then come back to this page.",
        isUser: false
    }))
    return{
        Navigation,
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
    padding: 10px 20px;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    background-color: #8bb4e0;
    margin-bottom: 20px;
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
        padding: 15px 30px;
    }
}
</style>