<template>
  <div class="tooltip-container">
    <svg
      
      @click="donateHedera"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="0 0 700 540"
      fill="currentColor"
      style="margin: 2rem; height: 2em;"
      title="Hedera Hashgraph (HBAR)"
    >
      <!-- Outer Circle -->
      <circle cx="256" cy="256" r="240" stroke="currentColor" stroke-width="42" fill="none"/>

      <!-- Left vertical bar -->
      <rect x="160" y="140" width="48" height="232" rx="8"/>

      <!-- Right vertical bar -->
      <rect x="304" y="140" width="48" height="232" rx="8"/>

      <!-- Top horizontal bar -->
      <rect x="160" y="176" width="192" height="40" rx="8"/>

      <!-- Bottom horizontal bar -->
      <rect x="160" y="296" width="192" height="40" rx="8"/>
    </svg>

    <span class="tooltip-text">donate hbar</span>
  </div>
</template>
<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
async function  donateHedera(){
    router.push('/donate');
}
</script>
