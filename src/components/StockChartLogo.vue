<template>
    <div class="tooltip-container">
      <svg @click="gotoTable" class="Table-container" style="margin: 2rem; height:2em" 
      
      xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" fill="currentColor"
      title="Stock Score Table">
        <path 
        d="M64 256l0-96 160 0 0 96L64 256zm0 64l160 0 0 96L64 416l0-96zm224 96l0-96 160 0 0 96-160 0zM448 256l-160 0 0-96 160 0 0 96zM64 32C28.7 32 0 60.7 0 96L0 416c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-320c0-35.3-28.7-64-64-64L64 32z"/>
      </svg>
      <span class="tooltip-text">Stock Chart</span>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { verifyToken } from '@/utils/auth';
const router = useRouter();
async function gotoTable(){
       
    router.push('/stockchart');
    }

</script>

<style scoped>
.Table-container {
    position: fixed;
    bottom: 180px;
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

.Table-container:hover {
    color: #3e3e3ece;
    /* Customize the icon color */
}
.tooltip-container {
    position: fixed;
    width: auto;
    bottom: 205px;
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