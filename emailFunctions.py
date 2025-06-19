import requests
import os
import dotenv
import json
dotenv.load_dotenv()

def email_send(e_to,e_subject,e_body,e_content_type):
    tenant_id = os.getenv('TENANT_ID')
    client_secret = os.getenv('SECRET_VALUE')
    client_id = os.getenv('APP_ID')
    my_email = os.getenv('EMAIL')

    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"

    token_data={
        "client_id":client_id,
        "client_secret":client_secret,
        "scope":"https://graph.microsoft.com/.default",
        "grant_type":"client_credentials"
    }
    token_response = requests.post(token_url,data=token_data,headers={"Accept":"Application/json"});
    access_token = json.loads(token_response.text).get('access_token')
    if not access_token:
        return None
    graph_url= f"https://graph.microsoft.com/v1.0/users/{my_email}/sendMail"
    message={
        "message":{
            "subject":e_subject,
            "body":{
                "contentType":e_content_type,
                "content":e_body

            },
            "toRecipients":[
                {
                    "emailAddress":
                    {
                    "address":e_to
                    }
                }
            ]
        },
        "saveToSentItems":"true"
    }
    headers={
        "Authorization":f"Bearer {access_token}",
        "Content-Type":"Application/json"
    }
    graph_response = requests.post(graph_url,headers=headers,json=message)
    if graph_response.status_code==202:
        return "Success"
    else:
        return graph_response.text


email_send("jjmr86@live.com.mx","hi there","this is a body text","Text")
