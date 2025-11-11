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
          <input v-model="name" type="text" id="name" required placeholder="@name"/>
        </div>

        <div class="form-group">
          <label for="username">Username</label>
          <input v-model="username" type="text" id="username" required placeholder="@username"/>
        </div>

        <div class="form-group">
          <label for="email">Email</label>
          <input v-model="email" type="email" id="email" required placeholder="@email"/>
        </div>

        <div class="form-group">
          <label for="password">Password</label>
          <input v-model="password" type="password" id="regPassword" required placeholder="@password"/>
        </div>
        <div class="form-group">
          <label for="password2">Password</label>
          <input v-model="password2" type="password" id="regPassword2" required placeholder="@password repeat" />
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
      password2:'',
      errorMessage: '',
      successMessage: '',
      loading: false,
      router: useRouter(), // Use Vue Router for navigation
      showSuccessModal: false, // Control the visibility of the success modal
    };
  },
  methods: {
    async registerUser() {
          // Check if passwords match before proceeding
      if (this.password !== this.password2) {
        this.errorMessage = "Passwords do not match";
        return;
      }
      const passwordRegex = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$/;
      if (!passwordRegex.test(this.password)) {
        this.errorMessage = "Password must be at least 8 characters long, contain one uppercase letter, one lowercase letter, one number, and one special character.";
        return;
      }
      this.loading = true;
      try {
        const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/register`, {
          name: this.name,
          username: this.username,
          email: this.email,
          password: this.password
        });

        if (response.data.success) {
          
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
      this.router.push('/login'); // Redirect to the login page
    }
  }
};
</script>

<style scoped>


</style>
