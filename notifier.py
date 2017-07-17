import smtplib
from os.path import basename
from datetime import datetime
from email.utils import COMMASPACE, formatdate
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


def send_email(user, pwd, recipient, subject, body, attachments=[]):
    to = recipient if type(recipient) is list else [recipient]
    try:
        msg = MIMEMultipart()
        msg['From'] = user
        msg['To'] = COMMASPACE.join(to)
        msg['Date'] = formatdate(localtime=True)
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        for attachment in attachments:
            with open(attachment, 'rb') as f:
                image = MIMEImage(f.read(), basename(attachment))
                msg.attach(image)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        server.sendmail(user, to, msg.as_string())
        server.close()
        print('successfully sent the mail')
    except Exception as e:
        print("failed to send mail: {}".format(str(e)))


class Notifier():
    def __init__(self):
        self.user, self.pwd, self.to, self.device = self.get_config()

    def extract_value(self, string):
        return string.split(":")[1].strip()

    def get_config(self):
        user = None
        pwd = None
        to = None
        device = None
        lines = []
        with open('mail.config', 'r') as f:
            lines = f.readlines()
        for line in lines:
            if line.startswith('user'):
                user = self.extract_value(line)
            elif line.startswith('pwd'):
                pwd = self.extract_value(line)
            elif line.startswith('recipient'):
                to = self.extract_value(line)
            elif line.startswith('device'):
                device = self.extract_value(line)
        if not (user and pwd and to and device):
            message = """you must supply the:
              'user'
              'password'
              'recipient'
              'device'
            values in the config"""
            print(message)
        return user, pwd, to, device

    def send(self, subject, message=""):
        if self.user and self.pwd and self.to and self.device:
            subject = "{}: {}".format(self.device, subject)
            send_email(self.user, self.pwd, self.to, subject, message)

    def send_screenshots(self, filenames):
        if self.user and self.pwd and self.to and self.device:
            subject = "{}: {}".format(
                self.device,
                datetime.now().strftime("%c"))
            send_email(
                self.user,
                self.pwd,
                self.to,
                subject,
                "",
                filenames)
