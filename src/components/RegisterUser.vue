<template>
  <div v-if="loading" class="loading-overlay">
    <div class="loading-throbber">
      <div class="spinner"></div>
      <p class="centered-text">Creating User please wait...</p>
    </div>
  </div>
  <div>
    <div class="registration-container">
      <h1>Create a New Account</h1>

      <!-- Display error message if any -->
      <div v-if="errorMessage" class="error-message">
        <p>{{ errorMessage }}</p>
      </div>
      <form @submit.prevent="registerUser">
        <div class="form-group">
          <label for="name">Name</label>
          <input v-model="name" type="text" id="name" required autocomplete="name"/>
        </div>

        <div class="form-group">
          <label for="username">Username</label>
          <input v-model="username" type="text" id="regUsername" required autocomplete="regUsername"/>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input v-model="email" type="email" id="email" required autocomplete="email"/>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input v-model="password" type="password" id="regPassword" required />
        </div>
        <div v-if="!showSuccessModal" class="modal-overlay">
        <button type="submit">Register</button>
        </div>
      </form>
      <div>
      <!-- Success Modal -->
      <div v-if="showSuccessModal" class="modal-overlay">
        <div class="modal">
          <p>{{ successMessage }}</p>
          <button @click="redirectToLogin">OK</button>
        </div>
      </div>
    </div>
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
      router: useRouter(), // Use Vue Router for navigation
      showSuccessModal: false, // Control the visibility of the success modal
    };
  },
  methods: {
    async registerUser() {
      this.loading = true;
      try {
        const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/register`, {
          name: this.name,
          username: this.username,
          email: this.email,
          password: this.password
        });

        if (response.data.success) {
          console.log("register success ",response.data.message)
          this.successMessage = 'User created successfully! You will be redirected to the login page.';
          this.errorMessage = '';
          this.loading = false;
          this.showSuccessModal = true; // Show the modal
        } else {
          this.errorMessage = response.data.message;
          this.successMessage = '';
        }
      } catch (error) {
        this.errorMessage = error.response ? error.response.data.message : 'An error occurred.';
        this.successMessage = '';
        this.loading = false;
      }
    },
    redirectToLogin() {
      this.showSuccessModal = false; // Hide the modal
      this.router.push('/'); // Redirect to the login page
    }
  }
};
</script>

<style scoped>
h1{
  position:relative;
  width: auto;
  align-items: top;
  justify-content: top;
  color: #767676c4;
  font-size: 15px;
}

html, body {
  margin: 0;
  padding: 0;
  overflow: hidden; /* Prevents scrollbars from appearing */
  width: 100vw;
}

.registration-container{
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
}

.form-group input{
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

</style>