<template>
    <h1>
        Quarterly Stock Trend
    </h1>
    <h2>Message</h2>
    <td>
        the growth comparison in % is same q last year
    </td>
    <Navigation/>
  <div>
    <div >
      <div v-if="paginatedRecords.length" class="table-container">
        
        <div >
          <table>
            <thead>
              <tr>
                <th @click="sortTable('ticker')">Symbol<span class="sortClass"></span></th>
                <th @click="sortTable('value')">Value in $ Billions <span class="sortClass"></span></th>
                <th @click="sortTable('trend')">last year q comparison in %<span class="sortClass"></span></th>
                <th @click="sortTable('total_score')">last 5 years stock score<span class="sortClass"></span></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in paginatedRecords" :key="index">
                <td>{{ record['ticker'] }}</td>
                <td>{{ record['value'] }}</td>
                <td>{{ record['trend'] }}%</td>
                <td>{{ record['score'] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination-controls">
          <button @click="previousPage" :disabled="currentPage === 1" class="buttons">Prev</button>

          <span>Page {{ currentPage }} of {{ totalPages }}</span>

          <!-- Input for page navigation -->
          <input type="number" v-model.number="enteredPage" @keyup.enter="goToPage" :min="1" :max="totalPages"
            placeholder="@page" class="terminal-input"/>
          <button @click="goToPage" class="buttons">Go</button>

          <button @click="nextPage" :disabled="currentPage === totalPages" class="buttons">Next</button>
        </div>
      </div>
      <!-- Loading Throbber -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-throbber">
          <div class="spinner"></div>
          <p>Getting quarterly data...</p>
        </div>
      </div>
    </div>
  </div>

</template>

<script>

import axios from 'axios';
import {ref,watch,onMounted,computed} from 'vue';
import Navigation from '@/components/Navigation.vue';
export default{
    props:{
    itemsPerPage: {
      type: Number,
      default: 100,
    },
},
    components:{
        Navigation,
    },
    setup(props){
        const currentPage = ref(1);
    const totalSymbols = ref();
    const enteredPage = ref(currentPage.value); // Store entered page number
    const totalPages = ref(10); // Replace with actual total pages logic
    const loading = ref(false);
    const stocks = ref([]);
    const flatRecords = ref([]); // Flattened array of records


    const sortKey = ref(''); 
    const sortOrder = ref(1); 
    const sortTable = (key) => { if (sortKey.value === key) { 
      
      sortOrder.value = -sortOrder.value; 
      // Reverse order if same column is sorted again 
      } 
      else { 
        sortKey.value = key; 
        sortOrder.value = 1; // Default order to ascending 
        } 
      };
    
      const sortedRecords = computed(() => { 
        const sorted = flatRecords.value.slice().sort((a, b) => { 
          if (a[sortKey.value] < b[sortKey.value]) 
          return -sortOrder.value; if (
        a[sortKey.value] > b[sortKey.value]) 
        return sortOrder.value; return 0; 
      }); 
      return sorted; 
    });
    const paginatedRecords = computed(() => {
      const start = (currentPage.value - 1) * props.itemsPerPage;
      const end = start + props.itemsPerPage;
      return sortedRecords.value.slice(0, 100);
    });


    // Watch for changes in currentPage and fetch data for the new page
    watch(currentPage, (newPage) => {
      fetchData(newPage);
    });


    // Fetch data from API and flatten it for pagination
    const fetchData = async (page = 1) => {
      loading.value = true;

      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/AllQStockTrend`, {
          params: { page, page_size: props.itemsPerPage },
        });
        
        

        // Assign fetched data to stocks
        if (response.data.data && typeof response.data.data === 'object') {
          stocks.value = response.data.data;
          totalSymbols.value = response.data.total_symbols;
          totalPages.value=Math.ceil(totalSymbols.value/100)
          
          
          // Flatten the structure
          flatRecords.value = Object.entries(stocks.value).flatMap(([symbol, records]) => {
            return records.map(record => ({ symbol, ...record }));
          });
        } else {
          console.error('API response is not in the expected format:', response.data.data);
          stocks.value = {};
          flatRecords.value = [];
          totalSymbols.value = 0;
        }
      } catch (error) {
        console.error('Error fetching data:', error);
      }
      loading.value = false;
    };


    const nextPage = () => {
      if (currentPage.value < totalPages.value) currentPage.value++;
    };
    const previousPage = () => {
      if (currentPage.value > 1) currentPage.value--;
    };
    const goToPage = () => {
      if (enteredPage.value >= 1 && enteredPage.value <= totalPages.value) {
        currentPage.value = enteredPage.value;
      } else {
        alert(`Please enter a page number between 1 and ${totalPages.value}`);
      }
    };

    onMounted(() => {
      fetchData();


    });
    return {
      currentPage,
      totalPages,
      nextPage,
      previousPage,
      loading,
      fetchData,
      stocks,
      sortedRecords,
      paginatedRecords,
      goToPage,
      sortTable,
      enteredPage
    };
  },

};



</script>
<style scoped>

 </style>