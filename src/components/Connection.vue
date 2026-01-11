<template>
  
  <span>eacsa> </span>
    wallet details:
   address: {{ address }}
    chainId: {{ chainId }}
    status: {{ status }}
  
  <button v-if="status !== 'disconnected'" type="button" @click="disconnect.mutate()"
  class="buttons">
    disconnect
  </button>
  
</template>
<script setup lang="ts">
import {useConnection, useDisconnect } from '@wagmi/vue'

const { address, chainId, status } = useConnection()
const  disconnect  = useDisconnect()
</script>


