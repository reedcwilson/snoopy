import logging
import requests
import base64
from os import getenv
from os.path import basename, join
from datetime import datetime


bad_config_message = """you must supply the:
  'user'
  'password'
  'recipient'
  'device'
  'token'
values in the config"""


def send_mailgun_message(domain, api_token, to, subject, body, attachments=[]):
    if getenv('EMAIL') == 'False':
        return
    files = []
    for name in attachments:
        with open(name, 'rb') as f:
            data = f.read()
            files.append(("attachment", (basename(name), data)))
    requests.post(
        "https://api.mailgun.net/v3/{}/messages".format(domain),
        auth=("api", api_token),
        files=files,
        data={"from": "Snoopy <snoopy@{}>".format(domain),
              "to": to,
              "subject": subject,
              "text": body,
              })


class Notifier():
    def __init__(self, secrets_manager, storage_directory):
        self.secrets_manager = secrets_manager
        self.config = self.get_config()
        self.storage_directory = storage_directory
        self._update_last_email()

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
                '{}\ntoken: {}\n'.format(message, self.get_token()))
            self._update_last_email()

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
            self._update_last_email()

    def _update_last_email(self):
        with open(join(self.storage_directory, 'last_email_sent'), 'w') as f:
            f.write(str(datetime.now()))

    def get_last_email(self):
        with open(join(self.storage_directory, 'last_email_sent'), 'r') as f:
            return datetime.strptime(f.read(), '%Y-%m-%d %H:%M:%S.%f')

    def ping(self):
        now = datetime.now()
        if (now - self.get_last_email()).days >= 7:
            self.send(subject='Ping', message=str(now))


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
