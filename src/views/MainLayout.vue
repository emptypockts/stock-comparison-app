<template>
    <h1 class="app-title">Welcome to Honcho</h1>
    <CompanyData @tickers-updated="updateTickers" />
    <ValueStockAnalysis :tickers="tickers"/>
    <StockFinancialCharts :tickers="tickers" />
    <IntrinsicValue :tickers="tickers"  />
    <RittenhouseAnalysis Analyis :tickers="tickers"  />

</template>
<script setup>
import { ref,watch } from 'vue';
import IntrinsicValue from '@/views/IntrinsicValue.vue';
import CompanyData from '@/views/CompanyData.vue';
import StockFinancialCharts from '@/views/StockFinancialCharts.vue';
import ValueStockAnalysis from '@/views/ValueStockAnalysis.vue';
import RittenhouseAnalysis from "@/views/RittenhouseAnalysis.vue";
import { useTickerStore } from '@/stores/tickerStore';
const tickers = ref([]);
const tickerStore=useTickerStore();
const updateTickers = (newTickers)=>{
 tickerStore.updateTickers(newTickers)
 tickers.value=tickerStore.currentTickers
}
</script>
