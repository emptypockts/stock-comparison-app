<template>
    <div class="tooltip-container">
      <svg @click="botTalk" class="botLogo-container" style="margin: 2rem; height:2em" 
      xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" fill="currentColor"
      title="ai with gemini flash">
        <path 
        d="M320 0c17.7 0 32 14.3 32 32l0 64 120 0c39.8 0 72 32.2 72 72l0 272c0 39.8-32.2 72-72 72l-304 0c-39.8 0-72-32.2-72-72l0-272c0-39.8 32.2-72 72-72l120 0 0-64c0-17.7 14.3-32 32-32zM208 384c-8.8 0-16 7.2-16 16s7.2 16 16 16l32 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-32 0zm96 0c-8.8 0-16 7.2-16 16s7.2 16 16 16l32 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-32 0zm96 0c-8.8 0-16 7.2-16 16s7.2 16 16 16l32 0c8.8 0 16-7.2 16-16s-7.2-16-16-16l-32 0zM264 256a40 40 0 1 0 -80 0 40 40 0 1 0 80 0zm152 40a40 40 0 1 0 0-80 40 40 0 1 0 0 80zM48 224l16 0 0 192-16 0c-26.5 0-48-21.5-48-48l0-96c0-26.5 21.5-48 48-48zm544 0c26.5 0 48 21.5 48 48l0 96c0 26.5-21.5 48-48 48l-16 0 0-192 16 0z"/>
      </svg>
      <span class="tooltip-text">power ai</span>
    </div>

</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
async function  botTalk(){
    router.push('/dashboard/ai');
}
</script>

<style scoped>
.botLogo-container {
    position: fixed;
    bottom: 100px;
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

.botLogo-container:hover {
    color: #3e3e3ece;
    /* Customize the icon color */
}
.tooltip-container {
    position: fixed;
    width: auto;
    bottom: 125px;
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