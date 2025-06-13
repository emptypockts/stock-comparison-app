import { defineStore } from "pinia";
export const useTickerStore=defineStore('tickerStore',{
    state:()=>({
        tickers:[]
    }),
    getters:{
        currentTickers:(state)=>state.tickers
    },
    actions:{
        updateTickers(newTickers){
            this.tickers=newTickers
        },
        deleteTickers(){
            this.tickers=[]
        }

    }
})