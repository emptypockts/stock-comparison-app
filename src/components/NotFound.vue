<template>
    <div class="page-not-found">
      <h1>Oops! Page Not Found</h1>
      <p>We can't seem to find the page you're looking for.</p>
      <router-link to="/">Go back to Home</router-link>
    </div>
  </template>
  
  <script>
  export default {
    name: 'PageNotFound',
  };
  </script>
  
  <style scoped>
  .page-not-found {
    text-align: center;
    padding: 50px;
  }
  
  .page-not-found h1 {
    font-size: 2.5em;
    margin-bottom: 20px;
  }
  
  .page-not-found p {
    font-size: 1.2em;
    margin-bottom: 20px;
  }
  
  .page-not-found a {
    color: #4CAF50;
    text-decoration: none;
    font-weight: bold;
  }
  
  .page-not-found a:hover {
    text-decoration: underline;
  }
  </style>
  