<template>
  <meta name="viewport" content="width=device-width, initial-scale=0.5">
  <div v-if="showAlert" class="modal">
    <div class="modal-content">
      <h2>Important Notice</h2>
      <div>
        <p>
          {{ showAlert }}
          Honcho is a demonstration application and is intended for educational and informational purposes only. The
          content and data provided within the application do not constitute financial advice, investment
          recommendations,
          or professional guidance. Users should not rely on Honcho for making financial decisions.
          I, as the creator of Honcho, am not responsible or liable for any losses, damages, or negative consequences
          that
          may arise from the use of this application. Always seek professional financial advice before making any
          investment or financial decisions.
          <br><br>
          p/b ratio is calculated using the Stockholders Equity instead of the tangible book value.
        </p>
        <button @click="dismissAlert">OK, got it</button>
      </div>
    </div>
  </div>
</template>

<script>
import { ref,onMounted } from 'vue';

export default {
  setup() {
    const showAlert = ref(true);
    onMounted(() => {
      // Check if cookies have been accepted or declined
      const isAlertAccepted = localStorage.getItem('loginAlert');
      if (isAlertAccepted) {
        showAlert.value = false;
      }
    });

    const dismissAlert = () => {

      localStorage.setItem('loginAlert', 'false')
      showAlert.value = false
    };

    return {
      showAlert,
      dismissAlert,
    };
  }
};
</script>

<style>
.modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.847);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  padding: auto;
  color: white;
  justify-content: center;
  align-items: center;
  background-color: rgba(78, 91, 110, 0.21);
  border-radius: 10px;
  text-align: center;
  width: 90%;

}

button {
  width: auto;
  padding: 10px;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  background-color: #dadcdc34;
  margin-top: 10px;
  margin-bottom: 10px;
}

button:hover {
  background-color: #8bb4e0;
}
</style>