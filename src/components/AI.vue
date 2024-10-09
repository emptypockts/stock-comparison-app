<template>
    <div>
        <div class="chat-header">
            <h1>AI Chat</h1>
        </div>
        <div class="chat-messages">
            <div v-for="(message, index) in messages" :key="index" class="message"
                :class="{ 'user-message': message.isUser }">
                {{ message.text }}
            </div>
        </div>
        <div class="chatty">
            <textarea v-model="userMessage" @keyup.enter="sendMessage" placeholder="Type a message..." rows="2"
                class="chatty-textarea">
                </textarea>
            <button @click="sendMessage">Send</button>
        </div>
        <div>
            <Logout />
            <GoBack />
        </div>
    </div>
</template>

<script setup>
import GoBack from './goBack.vue';
import Logout from './Logout.vue';
import { useRouter } from 'vue-router';
import { ref } from 'vue';
const router = useRouter();
const messages = ref([
    { text: 'Hello! How can I assist you?', isUser: false }
]);
const userMessage = ref('');

async function sendMessage() {
    if (userMessage.value.trim()) {
        messages.value.push({ text: userMessage.value, isUser: true });
        userMessage.value = '';
        setTimeout(() => {
            messages.value.push({ text: 'AI is thinking...', isUser: false });
        }, 1000);
    }
}


</script>

<style scoped>

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