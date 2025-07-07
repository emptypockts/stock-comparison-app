import { io } from "socket.io-client";
import { onMounted } from "vue";
let socket;
export function useSocket(){
    if(!socket){
        socket = io(import.meta.env.VITE_WS_SERVER,{
            transports:['websocket']
        });

    }
    const on = (event,callback)=>{
        socket.on(event,callback);
    }
    const off=(event,callback)=>{
        socket.off(event,callback);
    }
    const emit = (event,payload)=>{
        socket.emit(event,payload)
    }
    onMounted(()=>{
        socket?.disconnect();
        socket=null
    })
    return{
        socket,
        on,
        off,
        emit
    };
}
