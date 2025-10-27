<template>
    <div class="tooltip-container">
      <svg @click="gotoTable"  style="margin: 2rem; height:2em" 
      
      xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 512" fill="currentColor"
      title="Stock Score Table">
        <path 
        d="M64 256l0-96 160 0 0 96L64 256zm0 64l160 0 0 96L64 416l0-96zm224 96l0-96 160 0 0 96-160 0zM448 256l-160 0 0-96 160 0 0 96zM64 32C28.7 32 0 60.7 0 96L0 416c0 35.3 28.7 64 64 64l384 0c35.3 0 64-28.7 64-64l0-320c0-35.3-28.7-64-64-64L64 32z"/>
      </svg>
      <span class="tooltip-text">{{  tooltip  }}</span>
    </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
const router = useRouter();

const props = defineProps({
    route:{type:String, default:'/stockchart'},
    tooltip:{type:String,default:'Stock Chart'}
})

function gotoTable(){
       
    router.push(props.route);
    }

</script>

<style scoped>



</style>