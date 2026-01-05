<template>
    <div v-if="isLoading">loading</div>
    <div v-else-if="error">❌ {{ error }}</div>
    <div v-else>
      Balance: {{ formatted }}
  </div>
  <div>
  </div>
</template>
<script setup lang="ts">
import { useBalance } from '@wagmi/vue';
import { config } from '../config';
import { formatUnits } from 'viem';
import { computed} from 'vue';
const address = import.meta.env.VITE_ECDSA_TESTNET_EVM_ACCOUNT_ID as `0x${string}`

const { data, isLoading, error } =useBalance({
    address,
    config})
console.log(data.value)
const formatted =computed(()=>{
    if (!data.value)return null
    return formatUnits(data.value.value,data.value.decimals)

})


</script>
