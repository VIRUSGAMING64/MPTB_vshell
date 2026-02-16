import requests
import os.path as pth
from modules.compress.comp import Tar
from modules.utils import *
MB = 1024 * 1024
class MailHandler:
    def __init__(self, api_key, from_email="onboarding@resend.dev"):
        self.api_key = api_key
        self.from_email = from_email 
        self.api_url = "https://api.resend.com/emails"

    def send_file(self, to_mail, filepath :str= None):
        #! optimizar complejiddad espcial de esta funcion
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

class MailServer:
    def __init__(self):
        self.set = set()
        self.I = 0

    def upload(self,filename):
        size = pth.getsize(filename)
        if (size >= len(self.set) * 400 * MB):
            raise "File is large"
        count = split_path(filename, 5 * MB)

        try:
            for i in range(count):
                key,to_mail = self.GetNextMail()
                self.putmail(filename +"."+ str(i + 1, to_mail , key).zfill(3))
        except Exception as e:
            raise Exception(f"Error uploading file to [{to_mail}]:[{filename}.{str(i + 1).zfill(3)}]")


    def putmail(self,filename, uhmail, key):
        mail = MailHandler(key)
        mail.send_file(uhmail, filename)

    def GetNextMail(self):
        self.I += 1
        self.I %= len(self.set)
        l = []
        for x in self.set:
            l.append(x)

        return l[self.I]
    
    def add(self, key , uh_mail):
        self.set.add([key , uh_mail])