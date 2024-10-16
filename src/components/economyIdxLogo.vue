<template>
    <div class="tooltip-container">
      <svg @click="goToIdx" class="idxLogo-container" style="margin: 2rem; height:2em" 
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
const router = useRouter();
function goToIdx(){
    router.replace('/economyidx');

}
</script>

<style scoped>
.idxLogo-container {
    position: fixed;
    bottom: 140px;
    /* Distance from the bottom of the screen */
    right: 20px;
    /* Distance from the right of the screen */
    cursor: pointer;
    color: #6e6e6e8f;
    /* Customize the icon color */
    z-index: 1000;
    /* Ensure it's on top of other elements */
    transition: color 0.3s ease;
}

.idxLogo-container:hover {
    color: #3e3e3ece;
    /* Customize the icon color */
}
.tooltip-container {
    position: fixed;
    width: auto;
    bottom: 170px;
    /* Distance from the bottom of the screen */
    right: 140px;
    background: transparent;
}

.tooltip-text {
    visibility: hidden;
    width: 100px;
    color: #0000004b;
    text-align: center;
    border-radius: 5px;
    padding: 5px 0;
    position: absolute;
    z-index: 1;
    bottom: 125%; /* Position above the icon */
    left: 50%;
    margin-left: -50px;
    opacity: 0;
    transition: opacity 0.3s;
}

.tooltip-container:hover .tooltip-text {
    visibility: visible;
    opacity: 1;
}


</style>