import logging
import requests
import base64
from os.path import basename
from datetime import datetime


bad_config_message = """you must supply the:
  'user'
  'password'
  'recipient'
  'device'
  'token'
values in the config"""


def send_mailgun_message(domain, api_token, to, subject, body, attachments=[]):
    files = []
    for name in attachments:
        with open(name, 'rb') as f:
            data = f.read()
            files.append(("attachment", (basename(name), data)))
    return requests.post(
        "https://api.mailgun.net/v3/{}/messages".format(domain),
        auth=("api", api_token),
        files=files,
        data={"from": "Snoopy <snoopy@{}>".format(domain),
              "to": to,
              "subject": subject,
              "text": body,
              })


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
            elif line.startswith('api_token'):
                config['api_token'] = self.extract_value(line)
            elif line.startswith('domain'):
                config['domain'] = self.extract_value(line)
        if not self.is_valid(config):
            logging.error(bad_config_message)
        return config

    def get_token(self):
        token = self.config['token']
        now = str(datetime.now())
        blob = self.secrets_manager.encrypt('{} - {}'.format(token, now))
        return base64.b64encode(blob)

    def send(self, subject, message=""):
        if self.is_valid(self.config):
            subject = "{}: {}".format(
                self.config['device'],
                subject)
            send_mailgun_message(
                self.config['domain'],
                self.config['api_token'],
                self.config['to'],
                subject,
                '{}\ntoken: {}'.format(message, self.get_token()))

    def send_screenshots(self, filenames):
        if self.is_valid(self.config):
            subject = "{}: {}".format(
                self.config['device'],
                datetime.now().strftime("%c"))
            send_mailgun_message(
                self.config['domain'],
                self.config['api_token'],
                self.config['to'],
                subject,
                "token: {}".format(self.get_token()),
                filenames)


if __name__ == '__main__':
    import getpass
    domain = input("domain: ")
    to = input("to: ")
    api_token = getpass.getpass('api token:')
    send_mailgun_message(
        domain,
        api_token,
        to,
        'test',
        'this is a test',
        ['screens.zip'])
