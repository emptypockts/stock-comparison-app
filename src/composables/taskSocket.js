import { io } from "socket.io-client";
import { ref } from "vue";
import { generatePdfReport } from "@/utils/pdfOps";
import { fetch_reports } from "@/utils/fetch_reports";
const socket = io(import.meta.env.VITE_WS_SERVER,{
    secure:true
});
const isConnected = ref(false);
const taskData = ref(null);


export function useSocket(onTaskDone) {
    socket.on('connect', () => {
        isConnected.value = true;
    })
    socket.on('disconnect', () => {
        isConnected.value = false;
        console.log('my guy, you are no longer on')
    })
    socket.on('task_done', (data) => {
        const user_id = localStorage.getItem('user_id')
        taskData.value = data
        if (data.user_id==user_id){
            try {
          generatePdfReport(taskData.value.task_id, taskData.value.tickers, taskData.value.report_type)
        fetch_reports();
    }
    catch (err) {
        console.error('error trying to generate report', err)
    }   
}
    })
    return {socket,isConnected,taskData}
}

