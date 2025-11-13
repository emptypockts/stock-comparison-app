import { defineStore } from "pinia";
export const useLoadingStore=defineStore('loading',{
    state:()=>({
        loadingCount:0,
        pendingTasks:{}
    }),
    getters:{
        isLoading:(state)=>state.loadingCount>0

    },
    actions:{
        startLoading(){
            this.loadingCount++
        },
        stopLoading(){
            this.loadingCount--
            if (this.loadingCount<0) this.loadingCount=0
        },
        addTask(taskId){
            this.pendingTasks[taskId]=true
        },
        completeTask(taskId){
            delete this.pendingTasks[taskId]
        }
    }
})