import smtplib
from os.path import basename
from datetime import datetime
from email.utils import COMMASPACE, formatdate
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart


bad_config_message = """you must supply the:
  'user'
  'password'
  'recipient'
  'device'
  'token'
values in the config"""


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
    def __init__(self, secrets_manager):
        self.secrets_manager = secrets_manager
        self.config = self.get_config()

    def extract_value(self, string):
        return string.split(":")[1].strip()

    def is_valid(self, config):
        values = ['user', 'pwd', 'to', 'device', 'token']
        return all([True for value in values if value in config])

    def get_config(self):
        config = {}
        config_str = self.secrets_manager.get()
        lines = config_str.split("\n")
        for line in lines:
            if line.startswith('user'):
                config['user'] = self.extract_value(line)
            elif line.startswith('pwd'):
                config['pwd'] = self.extract_value(line)
            elif line.startswith('recipient'):
                config['to'] = self.extract_value(line)
            elif line.startswith('device'):
                config['device'] = self.extract_value(line)
            elif line.startswith('token'):
                config['token'] = self.extract_value(line)
        if not self.is_valid(config):
            print(bad_config_message)
        return config

    def send(self, subject, message=""):
        if self.is_valid(self.config):
            subject = "{}: {}".format(
                self.config['device'],
                subject)
            send_email(
                self.config['user'],
                self.config['pwd'],
                self.config['to'],
                subject,
                '{}\ntoken: {}'.format(message, self.config['token']))

    def send_screenshots(self, filenames):
        if self.is_valid(self.config):
            subject = "{}: {}".format(
                self.config['device'],
                datetime.now().strftime("%c"))
            send_email(
                self.config['user'],
                self.config['pwd'],
                self.config['to'],
                subject,
                "token: {}".format(self.config['token']),
                filenames)
