<template>
  <meta name="viewport" content="width=device-width, initial-scale=0.5">
  <div id="app">
      <div v-if="isLoading" class="loading-overlay">
    <div class="loading-throbber">
      <div class="spinner">
      </div>
    </div>
    </div>
       <router-view />
        <Navigation/>
          <CookieBanner />
          <LoginAlert />
    </div>
</template>

<script setup>
import CookieBanner from "@/components/CookieBanner.vue";
import LoginAlert from "@/components/LoginAlert.vue";
import Navigation from "@/components/Navigation.vue";   
import { useLoadingStore } from "@/stores/loadingStore"; 
import { computed,ref } from "vue";
const load_store=useLoadingStore()
const isLoading=computed(()=>load_store.isLoading);
</script>




<style scoped>


tr {
  background: transparent;
}

.navigation {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: rgba(76, 114, 237, 0);
}


button {
  background-color: #8bb4e0;
}

button:hover {
  background-color: #468eda;
}
</style>

<style>
* {
  font-family: monospace;
}

h1,
h2 {

  font-size: auto;
  margin-bottom: 20px;
  margin-left: 10px;
  color: #6d6d6d;
  text-align: left;
  font-weight: bold;

}

/* Loading overlay styles */
.loading-overlay {
position: fixed;
  backdrop-filter: blur(10px);
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}
.disabled-content{
  pointer-events: none;
  opacity: .5;
  filter: blur(5px);
}

.loading-throbber {
  text-align: center;
  color: white;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  width: 50px;
  height: 50px;
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.app-title {
  font-size: 2em;
  text-align: center;
  color: #6d6d6d;
  margin-bottom: 20px;
  font-weight: bold;
  width: 100%;
  /* Ensure it takes the full width */
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>