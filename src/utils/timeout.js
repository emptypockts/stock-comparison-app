export const showTempMessage = (ref,message,duration=3000)=>{
ref.value= message;
setTimeout(()=>{
    ref.value='';

},duration);
};