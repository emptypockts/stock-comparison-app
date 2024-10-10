<template>
  <div v-if="loading" class="loading-overlay">
    <div class="loading-throbber">
      <div class="spinner"></div>
      <p class="centered-text">Creating User please wait...</p>
    </div>
  </div>
  <div class="bg-image">
    <div class="registration-container">

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
        <div>
          <button @click=redirectToLogin class="button-goback">Go back</button>
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
          console.log("register success ")
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

.bg-image{
  background: repeat-y center url('https://images.unsplash.com/photo-1634117622592-114e3024ff27?q=80&w=2225&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D');
  height: 100vh; /* Make sure it covers the full height of the viewport */
  display: flex;
  justify-content: center;
  align-items: center;
}
button{
  width: auto;
  padding: 10px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background-color: #8bb4e0;
  margin-top: 10px;
  margin-bottom: 10px;

}
button:hover{
  background-color: #468eda;
}

.registration-container{
  padding: auto;
  color:white;
  justify-content: center;
  align-items: center;
  background-color:rgba(78, 91, 110, 0.21);
  border-radius: 10px;
  text-align: center;
}

.form-group input{

  width: 80%;
  padding: 10px;
  border: 0px;
  border-radius: 8px;
  background-color: rgba(81, 81, 81, 0.224); /*input background color */
}

input[type="submit"], button[type="submit"] {
  width: auto;
  padding: 10px;
  color:white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background-color: #8bb4e0;
  margin-top: 10px;
}

input[type="submit"]:hover, button[type="submit"]:hover {
  background-color: #468eda;
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
