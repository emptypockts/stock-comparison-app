<template>
  <meta name="viewport" content="width=device-width, initial-scale=0.5">
  <div id="app">
    <div v-if="isLoading" class="loading-overlay">
      <div class="loading-throbber">
        <div class="spinner">
        </div>
        <p>loading report please be patient...</p>
      </div>
    </div>
    <router-view />
  </div>
</template>
<script setup>
import { useLoadingStore } from "@/stores/loadingStore";
import { computed, ref } from "vue";
const load_store = useLoadingStore()
const isLoading = computed(() => load_store.isLoading);
</script>
<style>
</style>