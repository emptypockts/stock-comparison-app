<template>
    <div v-if="isLoading">loading</div>
    <div v-else-if="error">❌ {{ error }}</div>
    <div v-else>
        
            <span>eacsa> </span>
            balance: {{ balance }}
        
    </div>
    <div>
    </div>
</template>
<script setup lang="ts">
import { useBalance, useConnection } from '@wagmi/vue';
import { config } from '../config';
import { formatUnits } from 'viem';
import { computed } from 'vue';
const { address, isConnected } = useConnection({ config })

const { data, isLoading, error } = useBalance({
    address,
    config
})
console.log(data.value)
const balance = computed(() => {
    if (!isConnected.value || !data.value) return '0'
    return formatUnits(data.value.value, data.value.decimals)
})



</script>
