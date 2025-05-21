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
                <th @click="sortTable('Symbol')">Symbol<span class="sortClass"></span></th>
                <th @click="sortTable('Date')">Date<span class="sortClass"></span></th>
                <th @click="sortTable('Name')">Name<span class="sortClass"></span></th>
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
                <th v-if="!collapsed">Sum of Debt/FCF ratio Score</th>
                <th v-if="!collapsed">Market Cap Score</th>
                <th v-if="!collapsed">p/b ratio Score</th>
                <th v-if="!collapsed">p/e ratio Score</th>
                <th v-if="!collapsed">1.3 Earnings Yield Score</th>
                <th v-if="!collapsed">Dividends Yield Score</th>
                <th v-if="!collapsed">Earnings Yield Score</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(record, index) in paginatedRecords" :key="index">
                <td>{{ record['Symbol'] }}</td>
                <td>{{ record['Date'] }}</td>
                <td>{{ record['Name'] }}</td>
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
    isAuthenticated: Boolean, // Define isAuthenticated as a prop
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
      console.log("Sorting")
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
      console.log("Paginated Records Start:",start)
      console.log("Paginated Records End:",end)
      return sortedRecords.value.slice(0, 100); //Start and end is constant to 100 records 
    });

    // You can also watch isAuthenticated for changes
    watch(
      () => props.isAuthenticated,
      (newValue) => {
        console.log("isAuthenticated changed to:", newValue);
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
        console.log("Pages to query: ", page)
        console.log("Page size of query: ", props.itemsPerPage)

        // Assign fetched data to stocks
        if (response.data.data && typeof response.data.data === 'object') {
          stocks.value = response.data.data;
          totalSymbols.value = response.data.total_symbols;
          totalPages.value=Math.ceil(totalSymbols.value/100)
          console.log("Total Pages:",totalPages.value)
          console.log("This is the response data :", response.data)
          console.log("totalSymbols :", totalSymbols.value)
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
      console.log("Click go to page ",enteredPage.value)
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
  
  width: auto;
  justify-content: auto;
  padding: 8px;
  color: white;
  border: 1px;
  border-radius: 8px;
  cursor: pointer;
  background-color: #8bb4e0;
  
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