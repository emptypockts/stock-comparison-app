import { io } from "socket.io-client";
import { ref } from "vue";
import { fetch_reports } from "@/utils/fetch_reports";
import { useLoadingStore } from "@/stores/loadingStore";
import { useNotificationStore } from "@/stores/notificationStore";

// this function will be ignored until there is a real usecase. websocket service will be migrated to a poll service.

const user_id = localStorage.getItem('user_id')
const socket = io(`${import.meta.env.VITE_WS_SERVER}/ai`, {
    transports: ['websocket'], 
    autoConnect:false  
}
);

let registered = false;
const isConnected = ref(false);
const taskData = ref(null);
function getUserId(){
    return localStorage.getItem('user_id')
}

export function useSocket() {
    const notifStore = useNotificationStore();
    const loading = useLoadingStore();
    if (!registered) {
        registered = true;
        socket.on('connect', () => {
            const user_id = getUserId()
            console.log("socket id: ",socket.id, "user_id: ",user_id)
            socket.emit("join_room", { user_id })
            isConnected.value = true;
        })
        socket.on('disconnect', () => {
            isConnected.value = false;
            console.log('socket has been disconnected')
        })
        socket.on('task_done', async (data) => {
            console.log("task is completed")
            const user_id = getUserId();
            taskData.value = data
            if (taskData.value.user_id === user_id) {
                try {
                    await fetch_reports();
                    notifStore.add({
                        task_id: taskData.value.task_id,
                        tickers: taskData.value.tickers,
                        report_type: taskData.value.report_type
                    })
                }
                catch (err) {
                    console.error('error trying to fetch reports and notify store',err)
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
        socket.on('task_start', (data) => { console.log("task_start") })

    }
    const user_id = getUserId()
    if (user_id && !socket.connected){
        socket.auth={user_id}
        socket.connect()
    }
    return { socket, isConnected, taskData }
}

