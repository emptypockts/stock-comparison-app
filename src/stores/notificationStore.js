import { defineStore } from "pinia";
import { ref } from "vue";
export const useNotificationStore=defineStore("notifications",()=>{
    const list =ref([]);
    function add(alert){
        // {task_id,tickers,report_type}
        list.value.push(alert) 
    }
    function markRead(id){
        const item=list.value.find(n=>n.task_id==id)
        if (item)item.read=true;
    }
    function unreadCount(){
        return list.value.filter(n=>!n.read).length;
    }
    return {list,add,markRead,unreadCount};

});