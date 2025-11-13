<template>
  <h1>Value Stock Score Chart Hong Kong (HK)</h1>
  <h2>Message</h2>
  <td>
    The growth value is calculated from cash flow values. Any data fetch problem with the stock will cause the growth value default to 5%
  </td>
  <Navigation/>
  <div>
    <div >
      <div v-if="paginatedRecords.length" class="table-container">
              <button @click="toggleCollapse" class="buttons">
        ⟬⟬ expand/collapse ⟭⟭
      </button>
        <div >
          <table >
            <thead>
              <tr>
                <th @click="sortTable('Symbol')">Symbol<span class="sortClass"></span></th>
                <th @click="sortTable('Name')">Name<span class="sortClass"></span></th>
                <th @click="sortTable('Date')">Date<span class="sortClass"></span></th>
                <th @click="sortTable('Total Score')">Total Score<span class="sortClass"></span></th>
                <th @click="sortTable('Growth')">E_Growth 1Y<span class="sortClass"></span></th>
                <th v-if="!collapsed">Basic Average Shares</th>
                <th v-if="!collapsed">Basic EPS</th>
                <th v-if="!collapsed">Diluted EPS</th>
                <th v-if="!collapsed">Dividends</th>
                <th v-if="!collapsed">Dividends Yield</th>
                <th v-if="!collapsed">Earnings Yield</th>
                <th v-if="!collapsed">Free Cash Flow</th>
                <th v-if="!collapsed">Market Cap</th>
                <th v-if="!collapsed">Price Per Share</th>
                <th v-if="!collapsed">Tangible Book Value</th>
                <th v-if="!collapsed">Tangible Book Value Per Share</th>
                <th v-if="!collapsed">Total Debt</th>
                <th v-if="!collapsed">p/b ratio</th>
                <th v-if="!collapsed">p/e ratio</th>
                <th v-if="!collapsed">Debt FCF ratio</th>
                <th v-if="!collapsed">Sum of Debt/FCF ratio &gt 0 Score</th>
                <th v-if="!collapsed">Market Cap Score &gt 2B</th>
                <th v-if="!collapsed">p/b ratio &lt 2 Score</th>
                <th v-if="!collapsed">p/e ratio &lt 15 Score</th>
                <th v-if="!collapsed">1.3 Earnings Yield Score</th>
                <th v-if="!collapsed">Dividends Yield &gt 0 Score</th>
                <th v-if="!collapsed">Earnings Yield &gt 0 Score</th>
              </tr>
            </thead>
            <tbody>
              
              <tr v-for="(record, index) in paginatedRecords" :key="index">
                <td>{{ record['Symbol'] }}</td>
                <td>{{ record['Name'] }}</td>
                <td>{{ record['Date'] }}</td>
                <td>{{ record['Total Score'] }}</td>
                <td>{{ record['Growth'] }}</td>
                <td v-if="!collapsed">{{ record['Basic Average Shares'] }}</td>
                <td v-if="!collapsed">{{ record['Basic EPS'] }}</td>
                <td v-if="!collapsed">{{ record['Diluted EPS'] }}</td>
                <td v-if="!collapsed">{{ record['Dividends'] }}</td>
                <td v-if="!collapsed">{{ record['Dividends Yield'] }}</td>
                <td v-if="!collapsed">{{ record['Earnings Yield'] }}</td>
                <td v-if="!collapsed">{{ record['Free Cash Flow'] }}</td>
                <td v-if="!collapsed">{{ record['Market Cap'] }}</td>
                <td v-if="!collapsed">{{ record['Price Per Share'] }}</td>
                <td v-if="!collapsed">{{ record['Tangible Book Value'] }}</td>
                <td v-if="!collapsed">{{ record['Tangible Book Value Per Share'] }}</td>
                <td v-if="!collapsed">{{ record['Total Debt'] }}</td>
                <td v-if="!collapsed">{{ record['p/b ratio'] }}</td>
                <td v-if="!collapsed">{{ record['p/e ratio'] }}</td>
                <td v-if="!collapsed">{{ record['Debt FCF ratio'] }}</td>
                <td v-if="!collapsed">{{ record['Sum of Debt/FCF ratio Score'] }}</td>
                <td v-if="!collapsed">{{ record['Market Cap Score'] }}</td>
                <td v-if="!collapsed">{{ record['p/b ratio Score'] }}</td>
                <td v-if="!collapsed">{{ record['p/e ratio Score'] }}</td>
                <td v-if="!collapsed">{{ record['130pcnt_Earnings Yield Score'] }}</td>
                <td v-if="!collapsed">{{ record['Dividends Yield Score'] }}</td>
                <td v-if="!collapsed">{{ record['Earnings Yield Score'] }}</td>
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
          <p>getting annual score data...</p>
        </div>
      </div>
    </div>
  </div>

</template>

<script>
import axios from 'axios';
import { ref, watch, onMounted, computed } from 'vue';
import Navigation from '@/components/Navigation.vue';
export default {
  props: {
    itemsPerPage: {
      type: Number,
      default: 100,
    },
  },
  components:{
    Navigation,
  },
  setup(props) {
    const currentPage = ref(1);
    const totalSymbols = ref();
    const enteredPage = ref(currentPage.value); // Store entered page number
    const totalPages = ref(10); // Replace with actual total pages logic
    const loading = ref(false);
    const stocks = ref([]);
    const collapsed = ref(true); // Controls the visibility of extra columns
    const flatRecords = ref([]); // Flattened array of records
    const toggleCollapse = () => {
    collapsed.value = !collapsed.value;
    };

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
    let aValue = a[sortKey.value];
    let bValue = b[sortKey.value];
    
    // Parse percentages to numeric values if sorting `E_Growth 1Y`
    if (sortKey.value === "Growth") {
      aValue = parseFloat(aValue.replace('%', '')); // Convert to a number
      bValue = parseFloat(bValue.replace('%', ''));
    }
    
    // Perform the sorting
    if (aValue < bValue) return -sortOrder.value; 
    if (aValue > bValue) return sortOrder.value; 
    return 0; 
  }); 
  return sorted; 
});
    const paginatedRecords = computed(() => {
      const start = (currentPage.value - 1) * props.itemsPerPage;
      const end = start + props.itemsPerPage;
      
      return sortedRecords.value.slice(0, 100); //Start and end is constant to 100 records 
    });

    

    // Watch for changes in currentPage and fetch data for the new page
    watch(currentPage, (newPage) => {
      fetchData(newPage);
    });


    // Fetch data from API and flatten it for pagination
    const fetchData = async (page = 1,exchange="_HK") => {
      loading.value = true;

      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/fetchStockfromDB`, {
          params: { page, page_size: props.itemsPerPage,exchange:exchange},
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
      enteredPage,
      nextPage,
      previousPage,
      loading,
      fetchData,
      stocks,
      sortedRecords,
      paginatedRecords,
      goToPage,
      toggleCollapse,
      collapsed,
      sortTable,
    };
  },

};




</script>

<style scoped>

</style>