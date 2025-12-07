import { defineStore } from "pinia";
export const useLoadingStore=defineStore('loading',{
    state:()=>({
        loadingCount:0,
        pendingTasks:{},
        lastStatus:null
    }),
    getters:{
        isLoading:(state)=>state.loadingCount>0

    },
    actions:{
        startLoading(){
            this.loadingCount++
        },
        stopLoading(status="done"){
            this.loadingCount--
            if (this.loadingCount<0) this.loadingCount=0
            this.lastStatus=status;
        },
        addTask(taskId){
            this.pendingTasks[taskId]=true
        },
        completeTask(taskId,status="done"){
            delete this.pendingTasks[taskId]
            this.stopLoading(status)
        }
    }
})