<template>
    <div>
<div>
<input v-model="amount"/>
</div>
<div>
  <button
    @click="sendTx"
  >
    Send transaction {{ amount }}
  </button>
  </div>
      </div>
      {{ data }}
      {{ isPending }}
      {{ isSuccess }}
      {{ isError }}
      {{ error }}
</template>

<script setup lang="ts">
import { useSendTransaction } from '@wagmi/vue'
import { ref } from 'vue';
import { parseEther } from 'viem';

const amount = ref('')

const {
    mutate:sendTransaction,
    data,
    isPending,
    isSuccess,
    isError,
    error
}=useSendTransaction()
function sendTx(){
    if (!amount.value)return
    sendTransaction({
        to:'0x93fD0b92B09910077F96604880685cED9117adEe',
        value:parseEther(amount.value)
    })
}
</script>

