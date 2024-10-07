<template>
  <h1>Ticker Data </h1>
  <div class="input-container">
    <input v-model="ticker1" placeholder="Ticker 1" id="ticker 1" />
    <input v-model="ticker2" placeholder="Optional" id="ticker 2" />
    <input v-model="ticker3" placeholder="Optional" id="ticker 3" />
  </div>
  <div>
    <button @click="verifyAndFetchCompanyNames">Analyse</button>
  </div>

  <!-- Error message display -->
  <div v-if="errorMessage" class="error-message">
    <p>{{ errorMessage }}</p>

  </div>
  <div>
    <div v-if="companyNames">
      <ul class="list-container">
        <li v-for="(name, ticker) in companyNames" :key="ticker">
          <strong>Company:</strong> {{ ticker }}: {{ name[0] }}. <strong>Current price:</strong> ${{ name[1] }} <strong>
            Next Earnings:</strong> {{ name[2] }}<br><br>
        </li>
      </ul>
    </div>
  </div>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router'; // Import useRouter for navigation
import { nextTick } from 'vue';

export default {
  emits: ['tickers-updated', 'loading'], // Declare the custom events
  setup(props, { emit }) {
    const errorMessage = ref('');
    const ticker1 = ref('');
    const ticker2 = ref('');
    const ticker3 = ref('');
    const companyNames = ref({});
    const router = useRouter(); // Use Vue Router for navigation
    const verifyToken = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Session has expired. Please refresh the page and login again');
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
        router.push('/')
        return false;
      }
    };
    const fetchCompanyNames = async () => {
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
        const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/company_name`, {
          params: tickers.reduce((acc, ticker, index) => {
            acc[`ticker${index + 1}`] = ticker;
            return acc;
          }, {}),
        });


        companyNames.value = response.data;
        console.log("Company Names Object:", companyNames.value)
        const unknownCompany = Object.values(companyNames).includes('Unknown');
        if (unknownCompany) {
          errorMessage.value = "One or more ticker symbols are invalid. Please check your input."
          console.log("error is ", errorMessage.value)
          emit('loading', false); // Emit loading status as false to stop loading
          return errorMessage; // Stop further processing
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
    const verifyAndFetchCompanyNames = async () => {
      const isTokenValid = await verifyToken();
      console.log("Is token valid?: ", isTokenValid)
      if (isTokenValid) {
        fetchCompanyNames();
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
      fetchCompanyNames,
      companyNames,
      verifyAndFetchCompanyNames,
      errorMessage,
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

h1 {
  font-size: auto;
  margin-bottom: 20px;
  color: #333;
  text-align: left;
  font-weight: bold;
}
</style>