<template>
  <span>eacsa> </span>
  connect wallet
  <button v-for="connector in connectors" :key="connector.id" type="button" @click="connect.mutate({connector, chainId})" class="buttons">
    {{ connector.name}}
  </button>
</template>

<script setup lang="ts">
import { useChainId, useConnect, useConnectors } from '@wagmi/vue'
import { computed } from 'vue';
const allConnectors=useConnectors()
const chainId = useChainId()
const connect = useConnect()
const connectors = computed(()=>
allConnectors.value.filter(
  (c)=> c.name==='MetaMask'
)
)


</script>


