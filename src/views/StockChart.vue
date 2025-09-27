<template>
  <h1>Value Stock Score Chart</h1>
  <h2>Message</h2>
  <td>
    The growth value is calculated from cash flow values. Any data fetch problem with the stock will cause the growth value default to 5%
  </td>
  <Navigation/>
  <div>
    <div >
      <div v-if="paginatedRecords.length" class="table-container">
        <button @click="toggleCollapse">Click to expand or collapse</button>
        <div class="table-scroll">
          <table class="copyable-table">
            <thead>
              <tr>
                <th @click="sortTable('symbol')">ticker<span class="sortClass"></span></th>
                <th @click="sortTable('date')">date<span class="sortClass"></span></th>
                <th @click="sortTable('entity')">entity<span class="sortClass"></span></th>
                <th @click="sortTable('total_score')">total score<span class="sortClass"></span></th>
                <th @click="sortTable('fcf_cagr')">fcf compound growth 5y<span class="sortClass"></span></th>
                <th v-if="!collapsed">basic average shares</th>
                <th v-if="!collapsed">basic eps</th>
                <th v-if="!collapsed">diluted eps</th>
                <th v-if="!collapsed">dividends</th>
                <th v-if="!collapsed">dividends yield</th>
                <th v-if="!collapsed">earnings yield</th>
                <th v-if="!collapsed">fcf</th>
                <th v-if="!collapsed">market cap</th>
                <th v-if="!collapsed">price close</th>
                <th v-if="!collapsed">book value</th>
                <th v-if="!collapsed">total debt</th>
                <th v-if="!collapsed">pb ratio</th>
                <th v-if="!collapsed">pe ratio</th>
                <th v-if="!collapsed">debt fcf ratio</th>
                <th v-if="!collapsed">sum of debt/fcf ratio Score</th>
                <th v-if="!collapsed">market cap score</th>
                <th v-if="!collapsed">pb ratio score</th>
                <th v-if="!collapsed">pe ratio score</th>
                <th v-if="!collapsed">1.3 earnings yield score</th>
                <th v-if="!collapsed">dividends yield score</th>
                <th v-if="!collapsed">earnings yield score</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in paginatedRecords" :key="index">
                <td>{{ record['ticker'] }}</td>
                <td>{{ String(record['date']).slice(0,4) }}</td>
                <td>{{ record['entity'] }}</td>
                <td>{{ record['total_score'] }}</td>
                <td>{{ record['fcf_cagr'].toFixed(2) }}%</td>
                <td v-if="!collapsed">{{ record['WeightedAverageNumberOfSharesOutstandingBasic'] }}</td>
                <td v-if="!collapsed">{{ record['EarningsPerShareBasic'] }}</td>
                <td v-if="!collapsed">{{ record['EarningsPerShareDiluted'] }}</td>
                <td v-if="!collapsed">{{ record['PaymentsOfDividendsCommonStock'] }}</td>
                <td v-if="!collapsed">{{ record['dividend_yield'] }}</td>
                <td v-if="!collapsed">{{ record['earnings_yield'] }}</td>
                <td v-if="!collapsed">{{ record['fcf'] }}</td>
                <td v-if="!collapsed">{{ record['market_cap'] }}</td>
                <td v-if="!collapsed">{{ record['price_close'] }}</td>
                <td v-if="!collapsed">{{ record['book_value'] }}</td>
                <td v-if="!collapsed">{{ record['total_debt'] }}</td>
                <td v-if="!collapsed">{{ record['pb_ratio'] }}</td>
                <td v-if="!collapsed">{{ record['pe_ratio'] }}</td>
                <td v-if="!collapsed">{{ record['debt_fcf_ratio'] }}</td>
                <td v-if="!collapsed">{{ record['sum_debt_fcf_ratio_score'] }}</td>
                <td v-if="!collapsed">{{ record['market_cap_score'] }}</td>
                <td v-if="!collapsed">{{ record['pb_ratio_score'] }}</td>
                <td v-if="!collapsed">{{ record['pe_ratio_score'] }}</td>
                <td v-if="!collapsed">{{ record['1.3x_earnings_yield_score'] }}</td>
                <td v-if="!collapsed">{{ record['dividend_yield_score'] }}</td>
                <td v-if="!collapsed">{{ record['earnings_yield_score'] }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="pagination-controls">
          <button @click="previousPage" :disabled="currentPage === 1">Prev</button>

          <span>Page {{ currentPage }} of {{ totalPages }}</span>

          <!-- Input for page navigation -->
          <input type="number" v-model.number="enteredPage" @keyup.enter="goToPage" :min="1" :max="totalPages"
            placeholder="@page"/>
          <button @click="goToPage">Go</button>

          <button @click="nextPage" :disabled="currentPage === totalPages">Next</button>
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
    const fetchData = async (page = 1) => {
      loading.value = true;

      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/fetchStockfromDB`, {
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
.input-container{
width: 100px;
background: transparent;

}

input {
  width: 100px;
  padding: 8px;
  margin-top: 5px;
  border-radius: 8px;
  border: 1px solid #f1f0f0;
  background-color: #adadad1c;
  
}

input::placeholder {
  background-color: transparent;
}
button {
  position: relative;
  width: auto;
  justify-content: left;
  padding: 8px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
  background-color: #8bb4e0;
  margin-right: 10px;
}

button:hover {
    background-color: #468eda;
}
.table-container {
  overflow-x: auto; /* Enable horizontal scrolling if the table is too wide */
}
table {
  width: 90%;
  border-collapse: collapse;
}

thead th,
tbody td {
  padding: 10px;
  border: 1px solid #ddd;
  text-align: left;
  user-select: text;
  /* Ensure text can be selected */
}


tbody tr:hover {
  background-color: #f9f9f9;
  /* Optional: highlight row on hover */
}

/* Add CSS class to allow easy selection and copying */
.copyable-table {
  user-select: text;
  /* Ensure that table text can be selected for copying */
}

.title-container {
  justify-content: auto;
  /* Adjusts space between the title and the button */
  align-items: center;
  /* Vertically aligns the button and title */
}

.title-container h1 {
  margin-right: 10px;
  /* Optional: adds some space between the title and button */
}

.title-container button {
  margin-left: 10px;
  /* Optional: adds some space between the button and title */
  margin-top: 5px;
}

th {
  cursor: pointer; /* Change cursor to indicate clickability */
  position: relative; /* Position relative to contain the sorting indicator */
}

th span {
  display: inline-block;
  margin-left: 5px; /* Space between column name and sort indicator */
}

.asc::after {
  content: '▲'; /* Up arrow for ascending */
  font-size: 12px;
  position: absolute;
  right: 8px;
}

.desc::after {
  content: '▼'; /* Down arrow for descending */
  font-size: 12px;
  position: absolute;
  right: 8px;
}

.sortClass {
  background-color: #f1f1f1; /* Light background for sorted column */
}
.pagination-controls {
  position: fixed; /* Keeps it fixed on the screen */
  bottom: 10px;    /* Position it 10px from the bottom */
  left: 45%;       /* Center horizontally */
  transform: translateX(-50%); /* Centering adjustment */
  background-color: #fff; /* Optional: Background color */
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); /* Optional: Add some shadow */
  padding: 10px; /* Padding for better appearance */
  z-index: 1000; /* Ensure it appears above other elements */
  border-radius: 8px; /* Optional: Rounded corners */
}

</style>