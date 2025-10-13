import { ref } from 'vue';
import axios from 'axios';
const ai_reports=ref({});
export async function fetch_reports() {
    try {
        const data = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/v1/user_reports`, {
            params: {
                user_id: localStorage.getItem('user_id'),
            }
        })
        ai_reports.value = data.data.data
    } catch (err) {
        console.error("error: ", err)
    }
    return ai_reports.value
}
export {ai_reports}