<template>
    <div class="tooltip-container">
      <svg @click="goToIdx"  style="margin: 2rem; height:2em" 
      xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" fill="currentColor"
      title="Economy Index">
        <path 
        d="M32 32c17.7 0 32 14.3 32 32l0 336c0 8.8 7.2 16 16 16l400 0c17.7 0 32 14.3 32 32s-14.3 32-32 32L80 480c-44.2 0-80-35.8-80-80L0 64C0 46.3 14.3 32 32 32zM160 224c17.7 0 32 14.3 32 32l0 64c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-64c0-17.7 14.3-32 32-32zm128-64l0 160c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-160c0-17.7 14.3-32 32-32s32 14.3 32 32zm64 32c17.7 0 32 14.3 32 32l0 96c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-96c0-17.7 14.3-32 32-32zM480 96l0 224c0 17.7-14.3 32-32 32s-32-14.3-32-32l0-224c0-17.7 14.3-32 32-32s32 14.3 32 32z"/>
      </svg>
      <span class="tooltip-text">Economy Index</span>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { verifyToken } from '@/utils/auth';
const router = useRouter();

async function goToIdx(){
    router.push('/economyidx');
    
}
</script>

<style scoped>

</style>