<template>
    <div v-if="!cookieAccepted" class="cookie-banner">
      <p>
        We use cookies to improve your experience on our site. By using our site, you consent to our use of cookies.
      </p>
      <button @click="acceptCookies">OK, got it</button>
      <button @click="declineCookies">Decline</button>

    </div>
  </template>
  
  <script>
  import { ref, onMounted } from 'vue';
  
  export default {
    setup() {
      const cookieAccepted = ref(false);
  
      onMounted(() => {
      // Check if cookies have been accepted or declined
      const isAccepted = localStorage.getItem('cookieAccepted');
      if (isAccepted || localStorage.getItem('cookieDeclined')) {
        cookieAccepted.value = true;
      }
    });
  
      const acceptCookies = () => {
        // Set the cookieAccepted flag in localStorage
        localStorage.setItem('cookieAccepted', 'true');
        cookieAccepted.value = true;
        const timestamp = new Date().toISOString(); // Current timestamp
        localStorage.setItem('cookieAcceptedTimestamp', timestamp);

      };

      const declineCookies = () => {
      // Store a flag indicating the user has declined cookies
      localStorage.setItem('cookieDeclined', 'true');
      localStorage.removeItem('token');
      localStorage.removeItem('tokenExpiration')
      localStorage.removeItem('cookieAccepted')
      localStorage.removeItem('cookieAcceptedTimestamp')
      localStorage.removeItem('cookieDeclined')
      cookieAccepted.value = true; // Hide the banner
      alert('Session has expired. Please refresh the page and login again');
      router.replace('/');
    };
  
      return {
        cookieAccepted,
        acceptCookies,
        declineCookies,
      };
    },
  };
  </script>
  
  <style scoped>
  .cookie-banner {
    position: fixed;
    bottom: 0;
    width: 100%;
    background-color: #33333377;
    color: white;
    padding: 10px;
    text-align: center;
  }
  .cookie-banner p {
    display: flex;
    width: 90%;
    justify-content: center;

  }
  .cookie-banner button {
    background-color: #f1c40f;
    border: none;
    color: rgb(0, 0, 0);
    padding: 5px 10px;
    cursor: pointer;
    margin-left: 10px;
  }
  </style>
  