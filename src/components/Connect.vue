<template>
  <span>eacsa> </span>
  connect wallet
  <button v-for="connector in connectors" 
  :key="connector.id" 
  type="button" 
  @click="connect.mutate({connector, chainId})" 
  class="buttons">
    {{ connector.name}}
  </button>
</template>


<script setup lang="ts">

import { useChainId, useConnect, useConnectors } from '@wagmi/vue'
import { computed } from 'vue';
const isIos= /iPad|iPhone|iPod/.test(navigator.userAgent)
const allConnectors=useConnectors()
const chainId = useChainId()
const connect = useConnect()
const connectors = computed(()=>
allConnectors.value.filter((c)=>{ 
  if (isIos){
    return c.id==='walletConnect'
  }
  return c.id==='metaMaskSDK'
}
)
)


</script>


