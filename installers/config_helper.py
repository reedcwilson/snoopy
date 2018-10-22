import sys
import getpass
import os
import base64

_directory = os.path.dirname(os.path.abspath(__file__))
parentdir = os.path.dirname(_directory)
os.sys.path.insert(0, parentdir)
from src.lib.secrets_manager import SecretsManager

mail_config = 'src/mail.config'


def extract_value(string):
    return string.split(":")[1].strip()


def load_inputs(filename):
    config = {}
    config_str = ""
    with open(filename, 'r') as f:
        config_str = f.read()
    lines = config_str.split("\n")
    for line in lines:
        if line.startswith('user'):
            config['user'] = extract_value(line)
        elif line.startswith('pwd'):
            config['pwd'] = extract_value(line)
        elif line.startswith('recipient'):
            config['recipient'] = extract_value(line)
        elif line.startswith('device'):
            config['device'] = extract_value(line)
        elif line.startswith('token'):
            config['token'] = extract_value(line)
        elif line.startswith('api_token'):
            config['api_token'] = extract_value(line)
        elif line.startswith('domain'):
            config['domain'] = extract_value(line)
    return config


class ConfigHelper:
    def __init__(self):
        self.secret_key = None

    def get_encoded_secret(self):
        if not self.secret_key:
            print("secret key not set -- did you call create_config first?")
            sys.exit(-1)
        return base64.b64encode(self.secret_key.encode()).decode()

    def create_config(self):
        inputs = {}
        # you can pass a mail.config filename to be faster
        if len(sys.argv) > 1:
            inputs = load_inputs(sys.argv[1])
        else:
            inputs['device'] = input("name of device: ")
            inputs['recipient'] = input("recipient of emails: ")
            inputs['domain'] = input("mailgun domain: ")
            inputs['api_token'] = getpass.getpass("mailgun api token: ")
            inputs['token'] = getpass.getpass("secret phrase: ")

        # create config
        config_str = ""
        for key, value in inputs.items():
            config_str += "{}:{}\n".format(key, value)

        # accept the secret encryption key
        self.secret_key = getpass.getpass("password (should not equal token): ")

        print("preparing files...")

        # encrypt the mail config
        secrets_manager = SecretsManager(self.secret_key, mail_config)
        secrets_manager.put(config_str)
