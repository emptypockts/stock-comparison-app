import { defineStore } from "pinia";
export const useTickerStore=defineStore('tickerStore',{
    state:()=>({
        tickers:[],
        companyNames:{}
    }),
    getters:{
        currentTickers:(state)=>state.tickers,
        currentNames:(state)=>state.companyNames
    },
    actions:{
        updateTickers(newTickers){
            this.tickers=newTickers
        },
        updateNames(newNames){
            this.companyNames=newNames
        },
        deleteTickers(){
            this.tickers=[]
        }

    }
})