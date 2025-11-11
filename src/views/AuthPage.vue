<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <div v-if="loading" class="loading-overlay">
    <div class="loading-throbber">
      <div class="spinner"></div>
      <p>Authenticating... Please wait. DB powered by MongoDB</p>
      <!-- <p>Outage with the finance API. Migrating API to another free platform  Apologies for the inconvenience</p> -->
    </div>
  </div>
  <div class="bg-image">
    <div class="auth-container" >  
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username</label>
          <input v-model="username"  placeholder="@username" required  />
        </div>
        <div class="input-group">
          <label for="password">Password</label>
          <input v-model="password"  type="password" placeholder="@password"   required />
        </div>
        <div>
          <button type="submit">Login</button>
        </div>
        <div>
          <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
        </div>
        <div>
        <button @click="goToRegister">Create Account</button>
      </div>
      </form>
    </div>
  </div>
</template>



<script>
import axios from 'axios'; // Import Axios for HTTP requests
import { ref } from 'vue'; // Import ref for reactive variables
import { useRouter } from 'vue-router'; // Import useRouter for navigation

export default {
  setup() {
    const username = ref(''); // Define email as a reactive variable
    const password = ref(''); // Define password as a reactive variable
    const errorMessage = ref(''); // Define errorMessage as a reactive variable
    const loading = ref(false); // Loading state for authentication
    const router = useRouter(); // Use Vue Router for navigation
    const clearErrorMessage = () => {
      errorMessage.value = ''; // Clear the error message
    };
    const handleLogin = async () => {
      // Start loading
      loading.value = true;
      try {
        const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/login`, {
          username: username.value,
          password: password.value,
        },
          {
            headers: {
              'Content-Type': 'application/json' 
            }
          });

        

        if (response.data.success) {
          // Store JWT in localStorage
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('tokenExpiration', response.data.expiresAt);
          
          // Redirect to the main app
          router.push('/');
        } else {
          errorMessage.value = 'Invalid username or password.';
        }

      } catch (error) {
        console.error('error decoding password: ',error)
        if (error.response && error.response.status === 404) {
          // Show invalid username or password message
          errorMessage.value = 'Invalid username or password.';
        } else {
          // Generic error message for network/server errors
          errorMessage.value = 'An error occurred. Please try again.';
        }
      } finally {
        loading.value = false; // Stop loading indicator
      }
    };
    const goToRegister = () => {
      // Redirect to the registration page
      
      router.push('/register');
    };

    return {
      username,
      password,
      errorMessage,
      handleLogin, // Make sure to return handleLogin for form submission
      loading,
      goToRegister,
      clearErrorMessage
    };
  },
};
</script>

<style scoped>


</style>