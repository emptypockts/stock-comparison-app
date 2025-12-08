import { io } from "socket.io-client";
import { ref } from "vue";
import { generatePdfReport } from "@/utils/pdfOps";
import { fetch_reports } from "@/utils/fetch_reports";
import { useLoadingStore } from "@/stores/loadingStore";
import { useNotificationStore } from "@/stores/notificationStore";

const socket = io(`${import.meta.env.VITE_WS_SERVER}/ai`, {
    transports: ['websocket'],
    secure: true,
});

let registered = false;
const isConnected = ref(false);
const taskData = ref(null);

export function useSocket() {
    const notifStore = useNotificationStore();
    const loading = useLoadingStore();
    if (!registered) {
        registered = true;
        socket.on('connect', () => {

            const user_id = localStorage.getItem('user_id')
            socket.emit("join_room", { user_id })
            console.log("socket client: socket connected with user_id: " + user_id)
            isConnected.value = true;
        })
        socket.on('disconnect', () => {
            isConnected.value = false;
            console.log('socket has been disconnected')
        })
        socket.on('task_done', (data) => {
            const user_id = localStorage.getItem('user_id')
            taskData.value = data
            if (taskData.value.user_id === user_id) {
                try {
                    fetch_reports();
                    notifStore.add({
                        task_id: taskData.value.task_id,
                        tickers: taskData.value.tickers,
                        report_type: taskData.value.report_type
                    })
                }
                catch (err) {
                    console.error('error trying to fetch reports and notify store')
                    loading.stopLoading("error")
                }
                finally {
                    loading.stopLoading()
                    loading.completeTask(taskData.value.task_id)
                }
            }
            else {
                console.log(`user_id from local storage: ${user_id} and user_id ${taskData.value.user_id} from task does not match`)
            }
        })
        socket.on('task_failed', (data) => {
            loading.stopLoading("error")
            loading.completeTask(data.task_id, "error")
            console.log(`error executing task ${data.task_id}`)
        })
        socket.on('task_start', (data) => { console.log("task_start", data) })

    }
    return { socket, isConnected, taskData }
}

