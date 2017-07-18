
from secrets_manager import SecretsManager

key = "SUPER_SECRET_KEY"
mgr = SecretsManager(key, 'windows_mail.config')

with open('mail.config.actual', 'r') as f:
    mgr.put(f.read())
