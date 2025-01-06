<template>
    <div class="tooltip-container">

    
<svg @click="goBack" class="goBack-container" style="margin: 2rem; height:2em"
    xmlns="http://www.w3.org/2000/svg" viewBox="0 0 576 512" fill="currentColor"
    title="goBack">
    <path 
    d="M575.8 255.5c0 18-15 32.1-32 32.1l-32 0 .7 160.2c0 2.7-.2 5.4-.5 8.1l0 16.2c0 22.1-17.9 40-40 40l-16 0c-1.1 0-2.2 0-3.3-.1c-1.4 .1-2.8 .1-4.2 .1L416 512l-24 0c-22.1 0-40-17.9-40-40l0-24 0-64c0-17.7-14.3-32-32-32l-64 0c-17.7 0-32 14.3-32 32l0 64 0 24c0 22.1-17.9 40-40 40l-24 0-31.9 0c-1.5 0-3-.1-4.5-.2c-1.2 .1-2.4 .2-3.6 .2l-16 0c-22.1 0-40-17.9-40-40l0-112c0-.9 0-1.9 .1-2.8l0-69.7-32 0c-18 0-32-14-32-32.1c0-9 3-17 10-24L266.4 8c7-7 15-8 22-8s15 2 21 7L564.8 231.5c8 7 12 15 11 24z"/>
    </svg>
    <span class="tooltip-text">Go back</span>
</div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

function goBack(){
    router.push('\App')
}
</script>

<style scoped>
.goBack-container {
    position: fixed;
    bottom: 60px;
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

.goBack-container:hover {
    color: #3e3e3ece;
    /* Customize the icon color */
}
.tooltip-container {
    position: fixed;
    width: auto;
    bottom: 85px;
    /* Distance from the bottom of the screen */
    right: 110px;
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