<template>
    <div v-if="loading" class="loading-overlay">
      <div class="loading-throbber">
        <div class="spinner"></div>
        <p class="centered-text">Creating User please wait...</p>
      </div>
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
          const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/auth/register`, {
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
  .registration-form {
    max-width: 400px;
    margin: 50px auto;
    padding: 20px;
    border: 1px solid #ccc;
    border-radius: 10px;
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
  