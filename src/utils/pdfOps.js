import axios from "axios";
import { useLoadingStore } from "@/stores/loadingStore";

export async function generatePdfReport(task,fileName=[],bucket_name=''){
     try{
            
            const response = await axios.post(`${import.meta.env.VITE_APP_API_URL}/api/v1/gemini/report`,{
                bucket_name:bucket_name,
                task_id:task
            },
            {
                responseType:'blob'
            })
            const blob = new Blob([response.data],{
                type:'application/pdf'
            })
            
            const objectUrl= URL.createObjectURL(blob)
            const link=document.createElement('a')
            link.href=objectUrl
            link.download=`${response.data.size}_${fileName.join('_')}_${bucket_name}.pdf`||'generic_report.pdf'
            document.body.appendChild(link)
            link.click()
            URL.revokeObjectURL(objectUrl)
            document.body.removeChild(link)
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
        
