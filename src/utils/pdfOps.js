import axios from "axios";
import { useLoadingStore } from "@/stores/loadingStore";

export async function generatePdfReport(task,fileName=[],bucket_name=''){
     try{
            
            await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini/report`,{
                bucket_name:bucket_name,
                task_id:task
            })
        }
        catch(err){
            console.error('error generating report ',err)
            throw err
            }
        finally{
            const loading = useLoadingStore(); 
            loading.stopLoading()
            loading.completeTask(task)
        }
    }
        
