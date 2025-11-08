<template>
  <meta name="viewport" content="width=device-width, initial-scale=0.5">
  <div id="app">
      <div v-if="isLoading" class="loading-overlay">

    <div class="loading-throbber">
      <div class="spinner">
      </div>
      <p>loading report please be patient...</p>
    </div>
    </div>
       <router-view />
    </div>
</template>

<script setup>   
import { useLoadingStore } from "@/stores/loadingStore"; 
import { computed,ref } from "vue";
const load_store=useLoadingStore()
const isLoading=computed(()=>load_store.isLoading);
</script>





<style>
html {
  background-color: black;
}
.tooltip-container {
  position: relative; /* Make this the positioning context */
  display: flex;
  flex-direction: column; /* Stack tooltip above icon */
  align-items: center;
  margin: 0 1rem; /* Space between icons in a row */
  background: transparent;
}

.tooltip-text {
  position: absolute; /* Position relative to the container */
  bottom: 0%; /* Place tooltip above the icon */
  left: 50%;
  transform: translateX(-50%);
  visibility: hidden;
  opacity: 0;
  padding: 4px 8px;
  white-space: nowrap;
  box-shadow: 0 2px 6px rgba(0,0,0,0.15);
  transition: opacity 0.3s ease;
  z-index: 2000;
}

.tooltip-container:hover .tooltip-text {
  visibility: visible;
  opacity: 1;
}

* {
  font-family: "JetBrains Mono", "Fira Code", monospace;
  color: gray;
}

h1,
h2 {

  font-size: auto;
  margin-bottom: 20px;
  margin-left: 10px;
  text-align: left;
  font-weight: bold;

}


.loading-overlay {
position: fixed;
  backdrop-filter: blur(10px);
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
.disabled-content{
  pointer-events: none;
  opacity: .5;
  filter: blur(5px);
}

.loading-throbber {
  text-align: center;
  color: white;
}

p,ul{
  margin-left: 10px;
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

.app-title {
  font-size: 2em;
  text-align: center;
  margin-bottom: 20px;
  font-weight: bold;
  width: 100%;
  /* Ensure it takes the full width */
  display: flex;
  justify-content: center;
  align-items: center;
  background:transparent;
}

button {
  position: relative;
  width: auto;
  justify-content: left;
  padding: 8px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  margin-top: 10px;
  background-color: #8bb4e0;
  margin-left: 10px;
}

button:hover {
    background-color: #468eda;
}

.container {
    border: blue;
    background: black;
}
.error-message {
    color: red;
    margin-top: 10px;
}

button {
    position: relative;
    width: auto;
    justify-content: left;
    padding: 8px;
    color: white;
    border: none;
    border-radius: 8px;
    cursor: pointer;
    margin-top: 10px;
    background-color: #8bb4e0;
    margin-right: 10px;
}
button:hover {
    background-color: #468eda;
}
button:disabled {
    background-color: #999;
    /* Gray out */
    opacity: 0.6;
    /* Faded */
    cursor: not-allowed;
}
.console-report {
  background: #000814;          
  padding: 20px;
  width: 90%;
  overflow-x: auto;
}
.console-title {
  color: #ff0015;
  font-size: 1.2rem;
  font-weight: bold;
  margin-top: 18px;
  border-left: 4px solid #00eaff;
  padding-left: 10px;
}

.console-paragraph {
  margin: 8px 0;
  line-height: 1.5;
  color: gray;
}

.console-bullets {
  margin: 8px 0 8px 20px;
  color:gray;
}

.console-bullets li::marker {
  color:gray;
}
@media screen and (max-width: 768px) {

  th,
  td {
    padding: 3px;
    font-size: 10px;
    background-color: transparent;
    font-family: "JetBrains Mono", "Fira Code", monospace;
    color: white;
  }
}
.table-container {
  overflow-x: auto;
  color: gray;
  background: black;
}
table {
  width: 100%;
  border-collapse: collapse;
}

tbody tr:hover {
  background-color: #f9f9f9;
}
.copyable-table {
  user-select: auto;
}
.title-container {
  justify-content: auto;
  align-items: center;
}
.title-container h1 {
  margin-right: 10px;
}
.title-container button {
  margin-left: 10px;
  margin-top: 5px;
}


</style>