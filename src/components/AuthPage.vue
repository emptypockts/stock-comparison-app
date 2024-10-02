<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <div v-if="loading" class="loading-overlay">
    <div class="loading-throbber">
      <div class="spinner"></div>
      <p>Authenticating... Please wait.</p>
    </div>
  </div>
  <h1>Honcho for Honchos</h1>
    <div class="auth-container">
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username">Username</label>
          <input v-model="username" id="username" placeholder="@username" required autocomplete="name" />
        </div>
        <div class="input-group">
          <label for="password">Password</label>
          <input type="password" id="password" v-model="password" required />
        </div>
        <div class="input-group">
          <button type="submit">Login</button>
        </div>
        <div>
          <p class="error-message" v-if="errorMessage">{{ errorMessage }}</p>
        </div>
      </form>
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
              'Content-Type': 'application/json' // Ensure Content-Type is set to application/json
            }
          });

        console.log("Response :", response)

        if (response.data.success) {
          // Store JWT in localStorage
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('tokenExpiration', response.data.expiresAt);
          console.log("Login successful, routing to the main app")
          // Redirect to the main app
          router.push('app');
        } else {
          errorMessage.value = 'Invalid username or password.';
        }

      } catch (error) {
        console.log(error);  // Debugging step
        if (error.response && error.response.status === 401) {
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


    return {
      username,
      password,
      errorMessage,
      handleLogin, // Make sure to return handleLogin for form submission
      loading,
      clearErrorMessage
    };
  },
};
</script>

<style scoped>
h1{
  position:absolute;
  width: auto;
  padding-left: 10%;
  align-items: center;
  justify-content: center;
  color: #767676c4;
}

input::placeholder{
  color: white;
  border:0px;
}
html, body {
  margin: 0;
  padding: 0;
  overflow: hidden; /* Prevents scrollbars from appearing */
  width: 100vw;
}


.auth-container {
  position: absolute;
  width: 100vw;
  height:92.5vh;
  background-color: rgba(110, 110, 110, 0.249); /* Semi-transparent background */
  padding: 30px;

  text-align: center;
  color:#ffffff;
  width: 20%;
  justify-content: center;
  align-items: center;
  display: flex;
}


.input-group input {
  width: 100%;
  padding: 10px;
  border: 0px;
  border-radius: 8px;
  background-color: rgba(255, 255, 255, 0.187);
  color: white
}

input[type="submit"], button[type="submit"] {
  width: auto;
  padding: 10px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background-color: #dcdada34;
  margin-top: 10px;
}

input[type="submit"]:hover, button[type="submit"]:hover {
  background-color: #8bb4e0;
}

.error-message {
  color: red;
  margin-top: 10px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(77, 76, 76, 0.66);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.loading-throbber {
  text-align: center;
  color: rgb(255, 255, 255);
  font-size: 20px;
  margin-top: 220px;
}

.spinner {
  border: 4px solid rgba(165, 155, 155, 0.269);
  border-top: 4px solid #74bc2c1d;
  border-radius: 50%;
  width: 40px;
  height: 40px;
  animation: spin 1s linear infinite;
  margin: 0 auto;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

</style>