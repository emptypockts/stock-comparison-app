import axios from "axios"
import { ref } from 'vue';
const usedCredits=ref(0)
const creditLimit =10
export  async function validateCredits(){
const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/v1/credits`, {

})
usedCredits.value = response.data.credits
if (usedCredits.value===creditLimit)return false
else return true
}
export {usedCredits,creditLimit}