<template>
  <h1>Ticker Data 
  </h1>
  <div class="input-container">
    <input v-model="ticker1" placeholder="Try:intc" id="ticker 1" />
    <input v-model="ticker2" placeholder="Try:axp" id="ticker 2" />
    <input v-model="ticker3" placeholder="Try:nvda" id="ticker 3" />
  </div>
  <div>
    <button @click="verifyAndFetchCompanyData">Analyse</button>
  </div>
  <!-- Error message display -->
  <div v-if="errorMessage" class="error-message">
    <p>{{ errorMessage }}</p>
  </div>
    
  <div>
    <div v-if="companyData">
      <ul class="list-container">
        <li v-for="(name, ticker) in companyData" :key="ticker">
          <strong>Company:</strong> {{ ticker }}: {{ name['gStockData']['name'] }}. <strong>Current price:</strong> ${{ name['gStockData']['current_price'] }} <strong>
            Last Filing :</strong> {{ name['last_filing_date'] }}<br><br>
        </li>
      </ul>
      </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; // Import useRouter for navigation
// import { nextTick } from 'vue';

export default {
  emits: ['tickers-updated', 'loading'], // Declare the custom events
  setup(props, { emit }) {
    const errorMessage = ref('');
    const ticker1 = ref('');
    const ticker2 = ref('');
    const ticker3 = ref('');
    const companyData = ref({});
    const router = useRouter(); // Use Vue Router for navigation
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Token not available in local storage. Please refresh the page and login again');
        return false;
      }

      try {
        const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/verify`, null, {
          headers: { token },
        });

        return response.data.success;
         
    
      } catch (error) {
        console.error('Error verifying token:',error.response.data.message);
        localStorage.removeItem('token');
        localStorage.removeItem('tokenExpiration')
        localStorage.removeItem('cookieAccepted')
        localStorage.removeItem('cookieAcceptedTimestamp')
        localStorage.removeItem('cookieDeclined')
        router.push('/')
        return false;
      }
    };
    const fetchCompanyData = async () => {
      const tickers = [ticker1, ticker2, ticker3].map(tickerRef => tickerRef.value).filter(Boolean);
      if (tickers.length === 0) {
        errorMessage.value = "Please enter at least one stock ticker."
        console.log("error is ", errorMessage.value)
        return errorMessage;
      }
      // Emit loading status as true to indicate loading has started
      errorMessage.value = ""
      emit('loading', true);

      console.log("tickers:", tickers)
      // Function to verify the token before fetching company names

      try {
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/company_data`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });


        companyData.value = response.data;
        console.log("Company Data Object:", companyData.value)
        if (!companyData.value || Object.keys(companyData.value).length === 0) {
          errorMessage.value = 'No data found for the entered tickers.';
        } else {
          const missingTickers = tickers.filter(
            ticker => !Object.keys(companyData.value).includes(ticker)
          );
          if (missingTickers.length > 0) {
            errorMessage.value = `Data for the following tickers is missing: ${missingTickers.join(', ')}.`;
          }
        }


        // Emit the tickers and company names to the parent component
        emit('tickers-updated', tickers);
      } catch (error) {
        errorMessage.value = "One or more ticker symbols are invalid. Please check your input."
        console.log("error is ", errorMessage.value)
        emit('loading', false);
        return errorMessage;
      }

      finally {
        // Emit loading status as false to stop loading after the request is complete
        emit('loading', false);

      }
    };
    // Wrapper function to verify the token before fetching company names
    const verifyAndFetchCompanyData = async () => {
      const isTokenValid = await verifyToken();
      console.log("Is token valid?: ", isTokenValid)
      if (isTokenValid) {
        fetchCompanyData();
      } else {
        console.log("Pushing to login")
        router.push('/').then(() => {
          console.log('Navigation successful');
        }).catch((error) => {
          console.error('Navigation failed:', error);
        });
      }
    };
    return {
      ticker1,
      ticker2,
      ticker3,
      fetchCompanyData,
      companyData,
      verifyAndFetchCompanyData,
      errorMessage
    };
  },
};
</script>
<style scoped>
.error-message {
  color: red;
  margin-top: 10px;
}

.loading-section {
  width: auto;
  height: auto;
  display: flex;
  align-items: center;
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 15px;
  color: white;
  font-size: 1.5em;
  z-index: 1000;

}

.input-container{
width: auto;
background: transparent;

}

input {
  width: auto;
  padding: 8px;
  margin-top: 5px;
  border-radius: 8px;
  border: 1px solid #f1f0f0;
  background-color: #adadad1c;
  row-gap: 10px;
  display: flex;
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
}

button:hover {
  background-color: #468eda;
}


ul {
  list-style-position: inside;
  /* Moves the bullet inside the content box */
  padding-left: 0;
  /* Removes additional padding */

}

.list-container {
  border-radius: 8px;
  width: 90%;
}

li {

  margin-left: 0;
  /* Ensure no left margin */
  padding-left: 0;
  /* Remove any extra padding on the left */


}

</style>