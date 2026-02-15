import requests
import os.path as pth

class MailHandler:
    def __init__(self, api_key, from_email="onboarding@resend.dev"):
        self.api_key = api_key
        self.from_email = from_email 
        self.api_url = "https://api.resend.com/emails"

    def send_file(self, to_mail, filepath :str= None):
        try:
            with open(filepath, "rb") as f:
                content_bytes = list(f.read())
        except Exception as e:
            raise Exception(f"Error reading file: {e}")

        payload = {
            "from": self.from_email,
            "to": [to_mail],
            "subject": "Sending a file from Bot",
            "html": f"<p>File sent: {pth.basename(filepath)}</p>",
            "attachments": [
                {
                    "content": content_bytes,
                    "filename": pth.basename(filepath)
                }
            ]
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(self.api_url, json=payload, headers=headers)
        if response.status_code not in [200, 201, 202]:
             raise Exception(f"Resend Error {response.status_code}: {response.text}")
        return response