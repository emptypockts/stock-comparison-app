<template>
<button @click="sendEmail">
send Email
</button>
</template>
<script setup>

import axios from 'axios';
const sendEmail = async()=>{
    const {data,error}=await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/send-email`);
    if (error.value){
        console.error('error',error);

    }
    else{
    }
}

</script>
