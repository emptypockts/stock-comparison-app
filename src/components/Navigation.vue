<template>
      <div class="icon-bar">
    <economyIdxLogo />
    <StockChartLogo />
    <QtrStockChartLogo />
    <GoBack />
    <HederaLogo/>
    <Logout/>
    
    </div>
    </template>

    <script>

import Logout from "./Log_out.vue";
import economyIdxLogo from "./economyIdxLogo.vue";
import GoBack from "./goBack.vue";
import StockChartLogo from "./StockChartLogo.vue";
import QtrStockChartLogo from "./QtrStockChartLogo.vue";
import HederaLogo from "./hederaLogo.vue";
    export default{
        components:{
            Logout,
            economyIdxLogo,
            GoBack,
            StockChartLogo,
            QtrStockChartLogo,
            HederaLogo
        },
    }

</script>
<style scoped>

</style>