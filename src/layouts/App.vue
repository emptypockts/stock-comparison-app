<template>
  <div>
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