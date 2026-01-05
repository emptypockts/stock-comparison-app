<script setup lang="ts">
import Connect from '@/components/Connect.vue';
import Connection from '@/components/Connection.vue';
import Balance from '@/components/Balance.vue';
import SendTransaction from '@/components/SendTransaction.vue';
import Navigation from '@/components/Navigation.vue';
</script>

<template>
  <Connection />
  <Balance />
  <Connect />>
  <SendTransaction />
  <div>
        <Navigation/>
      </div>
</template>