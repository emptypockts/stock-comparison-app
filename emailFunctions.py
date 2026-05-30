import os
import resend
from dotenv import load_dotenv
from google_auth_oauthlib.flow import Flow

load_dotenv()
def email_send(e_to:str,e_subject:str,e_body:str,e_content_type=None):
    try:
        resend.api_key = os.getenv("RESEND_API")
        params: resend.Emails.SendParams = {
        "from": "eacsa <noreply@eacsa.us>",
        "to": e_to,
        "subject":e_subject,
        "html": e_body
    }

        email = resend.Emails.send(params)
        return "success"
    except Exception as e:
        return f"error {e}"
    
    

    

if __name__=="__main__":
    e_to="jjmr86@live.com.mx"
    e_subject="his there"
    e_body="<strong>hi there</strong>"
    email_send(e_to,e_subject,e_body)
