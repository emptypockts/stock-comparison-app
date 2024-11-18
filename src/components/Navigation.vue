<template>
      <div v-if="isAuthenticated" class="navigation">
    <Logout />
    <BotLogo />
    <economyIdxLogo />
    <GoBack />
    <StockChartLogo />
  </div>
    </template>

    <script>

import Logout from "./Log_out.vue";
import BotLogo from "./botLogo.vue";
import economyIdxLogo from "./economyIdxLogo.vue";
import GoBack from "./goBack.vue";
import StockChartLogo from "./StockChartLogo.vue";
    export default{
        components:{
            Logout,
            BotLogo,
            economyIdxLogo,
            GoBack,
            StockChartLogo
        },
    setup (){
    const isAuthenticated = localStorage.getItem('isAuthenticated');
    return {
        isAuthenticated,

    }
}
    }
</script>
<style scoped>
.navigation {
  display: flex;
  gap: 10px;
  padding: 10px;
  background: rgba(76, 114, 237, 0);
}

</style>