<template>
    <Logout/>
    <BotLogo />
    <economyIdxLogo />
    <GoBack />
    <StockChartLogo />
    <QtrStockChartLogo />
    </template>

    <script>

import Logout from "./Log_out.vue";
import BotLogo from "./botLogo.vue";
import economyIdxLogo from "./economyIdxLogo.vue";
import GoBack from "./goBack.vue";
import StockChartLogo from "./StockChartLogo.vue";
import QtrStockChartLogo from "./QtrStockChartLogo.vue";
    export default{
        components:{
            Logout,
            BotLogo,
            economyIdxLogo,
            GoBack,
            StockChartLogo,
            QtrStockChartLogo
        },
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