import { useSocket } from "./useSocket";
export function taskSocket(taskId,onTaskDone){
    const {on}=useSocket();
    on('task_done',(data)=>{
        if (data.task_id===taskId){
            console.log('showing data from the task socket',data)
            console.log('showing taskId from the task socket',taskId)
            onTaskDone(data)
        }
    })

}