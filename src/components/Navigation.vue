<template>
      <div class="icon-bar">
    
    <economyIdxLogo />
    <GoBack />
    <StockChartLogo />
    <StockChartLogo route="/stockcharthk" tooltip="HK Stock Chart"/>
    <QtrStockChartLogo />
    <Logout/>
    </div>
    </template>

    <script>

import Logout from "./Log_out.vue";
import economyIdxLogo from "./economyIdxLogo.vue";
import GoBack from "./goBack.vue";
import StockChartLogo from "./StockChartLogo.vue";
import QtrStockChartLogo from "./QtrStockChartLogo.vue";
    export default{
        components:{
            Logout,
            economyIdxLogo,
            GoBack,
            StockChartLogo,
            QtrStockChartLogo
        },
    }

</script>
<style scoped>
.icon-bar {
  position: fixed;
  bottom: 10px;
  right: 10px;
  display: flex;
  flex-direction: column;  
  align-items: flex-end;
  z-index: 2000;
  gap:0.5rem;
}
</style>