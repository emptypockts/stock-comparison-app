<template>
    <div>
        <div class="chat-header">
            <h1>AI Chat</h1>
        </div>
        <div class="chat-messages">
            <div v-for="(message, index) in messages" :key="index" class="message"
                :class="{ 'user-message': message.isUser }"
                v-html="message.text" >
            </div>
        </div>
        <div class="chatty">
            <!-- <textarea v-model="userMessage" @keyup.enter="sendMessage" placeholder="Type a message..." rows="2"
                class="chatty-textarea" disabled>
                </textarea> -->
            <button @click="sendMessage">Send</button>
        </div>
        <div>
            <Logout />
            <GoBack />
        </div>
    </div>
</template>

<script setup>
import { defineProps } from 'vue';
import { ref, watch } from 'vue';
import GoBack from './goBack.vue';
import Logout from './Log_out.vue';
// import { useRouter } from 'vue-router';
import axios from 'axios';
const userMessage = ref('You are a financial expert that will conduct the 7power analysis framework from Hamilton Helmer about the company with ticker pltr. Layout each of the 7 powers and your conclusion of each. Include any URL for reference.');
const props = defineProps({
  tickers: {
    type: Array,
    required: true,
  },
});

// Watch for changes in tickers prop and update userMessage
watch(() => props.tickers, (newTickers) => {
    console.log("tickers: ",newTickers)
  if (newTickers.length > 0) {
    userMessage.value = `You are a financial expert that will conduct the 7power analysis framework from Hamilton Helmer about the company with ticker ${newTickers.join(', ')}. Layout each of the 7 powers and your conclusion of each. Include any URL for reference.`;
  }
});

// const router = useRouter();
const messages = ref([
    { text: 'I will conduct the 7power analysis for this ticker. If you want analysis for another, ticker just change the first ticker field in the main page. Hit send to start. ', isUser: false }
]);

async function sendMessage() {
    if (userMessage.value.trim()) {
        messages.value.push({ text: userMessage.value, isUser: true });
        try{
            console.log("Sending query")
        const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/chat`, {
            query:userMessage.value,
            ticker:'pltr',
        });
        userMessage.value = '';
        setTimeout(() => {
            let formattedResponse = response.data['assistant']
            .replace(/\* \*\*/g, '<br>')
            .replace(/\. \*\*/g, '<br>')
            .replace(/\:\*\*/g, '<br><br>')
            .replace(/\*\*/g, '<br><br>');
            
            formattedResponse = formattedResponse.trim(); // Remove any leading new line or space
            messages.value.push({ text: formattedResponse, isUser: false });
        }, 1000);
    }
        catch (error) {
            console.error('Error sending query',error);
    }
    }
    else(messages.value.push({text:"<br>This ticker has been analysed already. To do another analysis, change the ticker in the main page",
    isUser:false}))
}


</script>

<style scoped>
.input-container{
width: auto;
background: transparent;

}

input {
  width: auto;
  padding: 8px;
  margin-top: 5px;
  border-radius: 8px;
  border: 1px solid #f1f0f0;
  background-color: #adadad1c;
  row-gap: 10px;
  display: flex;
}
.user-message {
  align-self: flex-end;
  color: rgb(212, 85, 106);
  
}


h1 {

  font-size: auto;
  margin-bottom: 20px;
  margin-left: 10px;
  color: #333;
  text-align: left;
  font-weight: bold;
}

.page {
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    justify-content: left;
    align-items: center;
    background: repeat center url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=2225&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
}


.chatty {
    align-items: left;
    align-items: start;
    justify-content: left;
    height: 98vh;
    width: 98vw;
}




.chatty-textarea {
    margin-top: 10px;
    margin-left: 10px;
    flex: 1;
    padding: 10px;
    border-radius: 8px;
    border: none;
    resize: none;
    /* Prevents manual resizing */
    background-color: #555555b1;
    /* Background color */
    color: white;
    /* Text color */
    line-height: 1.5;
    text-align: left;
    width:90%
    /* Aligns text to the left */

}

.chat-textarea:focus {
    outline: none;
}



.chatty textarea::placeholder {
    color: rgba(255, 255, 255, 0.66);
    text-align: left;


}

h1 {
    font-size: auto;
    margin-bottom: 20px;
    color: #333;
    text-align: left;
    font-weight: bold;
}

button {
    display: block;
    width: auto;
    justify-content: auto;
    padding: 8px;
    color: white;
    border: 1px;
    border-radius: 8px;
    cursor: pointer;
    background-color: #8bb4e0;
    margin-left: 10px;
}

button:hover {
    background-color: #468eda;
}

.chat-messages {
    flex: 1;
    margin-left: 10px;
    padding: 10px;
    overflow-y: auto;
    border-radius: 8px;
    background-color: #000000c0;
    color: rgba(255, 255, 255, 0.66);
    line-height: 1.5;
    font-family: monospace;
    width: 90%;
}
</style>