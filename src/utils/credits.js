import axios from "axios"
import { ref } from 'vue';
const usedCredits=ref(0)
let creditLimit =10
export  async function validateCredits(){
const response = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/v1/credits`, {

})
usedCredits.value = response.data.credits

if (import.meta.env.VITE_DEV_FLAG==='1'){
    creditLimit=1000
}
if (usedCredits.value===creditLimit)return false
else return true
}
export {usedCredits,creditLimit}