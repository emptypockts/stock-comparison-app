import axios from "axios";
export async function pollTaskStatus({
    task_id,
    msInterval = 5000,
    maxAttempts = 50,
    onOngoing,
    onFailed,
    onCompleted,
    onTimeout
}) {
    let attempts = 0;
    let stopped = false;
    const stop = () => {
        stopped = true
    }
    const poll = async () => {
        if (stopped) return;
        attempts+=1
        try{
            console.log("task: ",task_id)
            const aiResponse = await axios.get(`${import.meta.env.VITE_APP_API_URL}/api/v1/${task_id.toString()}`)

            const data = aiResponse.data
            const status = data[0].status
            console.log("polling task: ",task_id, "status: ", data[0].status, "attempts: ",attempts)
            if (status === "completed"){
                stop();
                if (onCompleted){
                    await onCompleted(data)
                }
                return
            }
            if (status === "ongoing"){
                if (onOngoing){
                    await onOngoing(data)
                }
            }
            if (status === " failed"){
                if (onFailed){
                    await onFailed(data)
                }
                return
            }
            if (attempts>=maxAttempts){
                stop();
                if (onTimeout){
                    await onTimeout(data)
                }
                return
            }
            setTimeout(poll,msInterval);
        }catch(err){
            console.error("polling error",err)
            if (attempts>=maxAttempts){
                stop();
                if (onTimeout){
                    await onTimeout({
                        task_id,
                        status:"timeout",
                        error:err
                    })
                }
                return;
            }
            setTimeout(poll,msInterval)
        }
    };
    poll();
    return{
        stop
    };
}
