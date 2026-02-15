import yagmail
import os.path as pth

class MailHandler:
    def __init__(self, gmail, key):
        self.app = yagmail.SMTP(
            gmail, key
        )

    def send_file(self, to_mail, filepath :str= None):
        if pth.getsize(filepath) > 50*1024*1024:
            raise "No files more than a 50MB"
        self.app.send(
            to_mail,"Sending a file", f"file: {filepath}", filepath
        )

    def send_message(self, to_mail, mess : str):
        self.app.send(
            to_mail,"Sending a message",  mess
        )
