export const showTempMessage = (
    targetRef,
    message,
    type="info",
    duration=3000,
    callback=null
)=>{
    targetRef.value={
        text:message,
        type:type
    }
    setTimeout(()=>{
        targetRef.value=null
        if (callback) callback()
    },duration)
}