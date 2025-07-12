export const showTempMessage = (errorMessage,message,duration=3000)=>{
errorMessage.value= message;
setTimeout(()=>{
    errorMessage.value='';

},duration);
};