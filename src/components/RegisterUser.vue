<template>
    <div v-if="loading" class="loading-overlay">
      <div class="loading-throbber">
        <div class="spinner"></div>
        <p class="centered-text">Creating User please wait...</p>
      </div>
    </div>
    <div class="split-screen">
    <!-- Left side for the Unsplash image -->
    <div class="image-container">
      <img src="https://images.unsplash.com/photo-1573425873096-b034f660a85c?q=80&w=2130&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"/>
    </div>
    <div class="registration-form">
      <h2>Create a New Account</h2>
      
      <!-- Display error message if any -->
      <div v-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
      </div>
  
      <!-- Display success message if any -->
      <div v-if="successMessage" class="success-message">
        <p>{{ successMessage }}</p>
      </div>
  
      <form @submit.prevent="registerUser">
        <div class="form-group">
          <label for="name">Name</label>
          <input v-model="name" type="text" id="name" required />
        </div>
  
        <div class="form-group">
          <label for="username">Username</label>
          <input v-model="username" type="text" id="username" required />
        </div>
  
        <div class="form-group">
          <label for="email">Email</label>
          <input v-model="email" type="email" id="email" required />
        </div>
  
        <div class="form-group">
          <label for="password">Password</label>
          <input v-model="password" type="password" id="password" required />
        </div>
  
        <button type="submit">Register</button>
      </form>
    </div>
    </div>
  </template>
  
  <script>
  import axios from 'axios';
  import { useRouter } from 'vue-router'; // Import useRouter for navigation
  
  export default {
    data() {
      return {
        name: '',
        username: '',
        email: '',
        password: '',
        errorMessage: '',
        successMessage: '',
        loading: false,
        router : useRouter(), // Use Vue Router for navigation
      };
    },
    methods: {
      async registerUser() {
        this.loading=true;
        try {
          const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/register`, {
            name: this.name,
            username: this.username,
            email: this.email,
            password: this.password
          });
  
          if (response.data.success) {
            this.successMessage = response.data.message;
            this.errorMessage = '';
            this.router.push('/');
          } else {
            this.errorMessage = response.data.message;
            this.successMessage = '';
          }
        } catch (error) {
          this.errorMessage = error.response ? error.response.data.message : 'An error occurred.';
          this.successMessage = '';
          this.loading=false;
        }
      }
    }
  };
  </script>
  
  <style scoped>
/* Split screen layout */
.split-screen {
  display: flex;
  height: 100vh; /* Full screen height */
}
  /* Left side - Image */
.image-container {
  flex: 1; /* Takes up half the screen */
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f0f0f0; /* Light background if image fails */
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover; /* Ensures image covers the container without distortion */
}
  .registration-form {
  flex: 1; /* Takes up half the screen */
  max-width: 500px;
  margin: auto; /* Center the form vertically */
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  background-color: white;
  border-radius: 8px;
  }
  
  .form-group {
    margin-bottom: 20px;
  }
  
  label {
    display: block;
    margin-bottom: 5px;
  }
  
  input {
    width: 100%;
    padding: 8px;
    box-sizing: border-box;
  }
  
  button {
    display: block;
  width: auto;
  justify-content: center;
  padding: 10px;
  background-color: #007BFF;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  margin: 0 auto;
  }
  
  button:hover {
    background-color: #0056b3;
  }
  
  .error-message {
    color: red;
    margin-bottom: 20px;
  }
  
  .success-message {
    color: green;
    margin-bottom: 20px;
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
  </style>
  