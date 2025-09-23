import { io } from "socket.io-client";
import { ref } from "vue";
import { downloadPdfReport } from "@/utils/downloadReport";
const socket = io(import.meta.env.VITE_WS_SERVER,{
    secure:true
});
const isConnected = ref(false);
const taskData = ref(null);
export function useSocket() {
    socket.on('connect', () => {
        isConnected.value = true;
        console.log('my guy, you are on the ws server socketid ', socket)
    })
    socket.on('disconnect', () => {
        isConnected.value = false;
        console.log('my guy, you are no longer on')
    })
    socket.on('task_done', (data) => {
        console.log('my guy, task_done is completed. downloading report ', data)
        taskData.value = data
            try {
        downloadPdfReport(taskData.value.task_id, taskData.value.tickers, taskData.value.report_type)
    }
    catch (err) {
        console.error('error trying to generate report', err)
    }
    })

    return {socket,isConnected,taskData}
}

