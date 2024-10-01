<template>
  <div v-if="loading" class="loading-overlay">
    <div class="loading-throbber">
      <div class="spinner"></div>
      <p>Authenticating... Please wait.</p>
    </div>
  </div>

  <div class="split-screen">
    <!-- Left side for the Unsplash image -->
    <div class="image-container">
      <img
        src="https://images.unsplash.com/photo-1573425873096-b034f660a85c?q=80&w=2130&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D" />
    </div>

    <!-- Right side for the login form -->
    <div class="auth-container">
      <h2 class="centered-text">Login to Honcho</h2>
      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label for="username" >Username</label>
          <input v-model="username" id="username" label="Username" placeholder="@username" required autocomplete="name"/>
        </div>
        <div class="input-group">
          <label for="password" >Password</label>
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
/* Split screen layout */
.split-screen {
  display: flex;
  height: 100vh;
  /* Full screen height */
}

/* Left side - Image */
.image-container {
  flex: 1;
  /* Takes up half the screen */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f0f0;
  /* Light background if image fails */
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  /* Ensures image covers the container without distortion */
}

/* Right side - Login form */
.auth-container {
  flex: 1;
  /* Takes up half the screen */
  max-width: 500px;
  margin: auto;
  /* Center the form vertically */
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: white;
  border-radius: 8px;
}

.input-group {
  margin-bottom: 15px;
}

input {
  width: 100%;
  padding: 8px;
  margin-top: 5px;
  border-radius: 8px;
  border: 0px solid #ccc;
}

button {
  display: block;
  width: auto;
  justify-content: center;
  padding: 10px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin: 0 auto;
}

button:hover {
  background-color: #8bb4e0;
}

.error-message {
  color: red;
  margin-top: 10px;
}

/* Loading overlay styles */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
}

.loading-throbber {
  text-align: center;
  color: white;
}

.spinner {
  border: 4px solid rgba(255, 255, 255, 0.3);
  border-radius: 50%;
  border-top-color: white;
  width: 50px;
  height: 50px;
  animation: spin 1s ease-in-out infinite;
  margin: 0 auto;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.centered-text {
  text-align: center;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
}

.modal {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  text-align: center;
}
</style>
