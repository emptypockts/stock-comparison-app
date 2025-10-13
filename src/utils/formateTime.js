import { formatDistanceToNow,format } from "date-fns"
import {toZonedTime,getTimezoneOffset} from 'date-fns-tz'
export function formatDateAgo (date){
    
    const timeZone = Intl.DateTimeFormat().resolvedOptions().timeZone;
    const formattedDate= date;
    const zoneDate=toZonedTime(new Date(formattedDate),timeZone)
    return formatDistanceToNow(zoneDate)
    
}
