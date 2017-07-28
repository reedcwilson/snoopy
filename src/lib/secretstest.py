
from secrets_manager import SecretsManager

key = "pwd\n"
mgr = SecretsManager(key, 'mail.config')

with open('mail.config.actual', 'r') as f:
    mgr.put(f.read())
