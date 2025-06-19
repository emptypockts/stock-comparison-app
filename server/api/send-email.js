import "isomorphic-fetch";
import { ConfidentialClientApplication } from '@azure/msal-node';
import { Client } from "@microsoft/microsoft-graph-client";

const tenantId = import.meta.env.TENANT_ID;
const clientSecret = import.meta.env.SECRET_ID;
const clientId = import.meta.env.CLIENT_ID;
const userEmail = import.meta.env.EMAIL;
const recipient = "jjmr86@live.com.mx";

export default defineEventHandler (async(event)=>{
    const msalConfig = {
        auth: {
            clientId,
            authority: `https://login.microsoftonline.com/${tenantId}`,
            clientSecret
        },

    };


    const cca = new ConfidentialClientApplication(msalConfig);
    const tokenResponse = await cca.acquireTokenByClientCredential({
        scopes: ["https://graph.microsoft.com/default"]
    })

    if (!tokenResponse || !tokenResponse.accessToken) {
        console.error('failed to get token')
    }
    const graphClient = Client.init({
        authProvider: (done) => {
            done(null, tokenResponse.accessToken);
        }
    });

    const message ={
        subject: "hello",
        body:{
            contentType:"Text",
            content:"Hello amigos"
        },
        toRecipients:[
            {
                emailAddress:{address:recipient}
            }
        ],
    }
    try{
        await graphClient.api(`/users/${userEmail}/sendMail`).post({
            message,
            saveTosentItems:true
        });
        console.log('email sent successfully')
            return { success: true };

    }
    catch (err){
        console.error('error sending email:',err)
        return {error:err.message}

    }

})
