import { io } from "socket.io-client";
import { ref } from "vue";
import { generatePdfReport } from "@/utils/pdfOps";
import { fetch_reports } from "@/utils/fetch_reports";
import { useLoadingStore } from "@/stores/loadingStore";
import { showTempMessage } from "@/utils/showMessages";
import { useNotificationStore } from "@/stores/notificationStore";

const socket = io(import.meta.env.VITE_WS_SERVER, {secure: true});

let registered = false;
const isConnected = ref(false);
const taskData = ref(null);
const notification = ref(null);

export function useSocket() {
    const notifStore=useNotificationStore();
    const loading = useLoadingStore();
    if (!registered) {
        registered = true;

        socket.on('connect', () => {
            
            const user_id=localStorage.getItem('user_id')
            socket.emit("register_user",{user_id})
            isConnected.value = true;
            console.log(`socket has been connected with id: ${socket.id} and userid: ${user_id}`)
            
        })
        socket.on('disconnect', () => {
            isConnected.value = false;
            console.log('socket has been disconnected')
        })
        socket.on('task_done', (data) => {
            const user_id = localStorage.getItem('user_id')
            taskData.value = data
            if (data.user_id === user_id) {
                try {
                    generatePdfReport(taskData.value.task_id, taskData.value.tickers, taskData.value.report_type)
                    fetch_reports();
                    notifStore.add({
                        task_id:taskData.value.task_id,
                        tickers:taskData.value.tickers,
                        report_type:taskData.value.report_type
                    })
                }
                catch (err) {
                    console.error('error trying to generate report', err)
                    loading.stopLoading("error")
                }
            }
        })
        socket.on('task_failed',(data)=>{
            loading.stopLoading("error")
            showTempMessage(notification,`Notification,"error executing ai task ${data.error}`,"error")
        })


    }
    return { socket, isConnected, taskData }
}

