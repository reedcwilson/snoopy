
import base64
from datetime import datetime
from secrets_manager import Crypt

key = "pwd\n"
crypt = Crypt(key)

now = str(datetime.now())
token = 'untouched'

token_str = '{} - {}'.format(token, now)
cipher = crypt.encrypt(token_str)
print('cipher: ', base64.b64encode(cipher))

# with open('src/lib/blob', 'r') as f:
#     blob = f.read()

blob = "b'oz3w0ak8JIt1dVIriFfGdyb/0zFyKiV9haXd0CAqo3ZyB014UiynhRx6iS+mbN+7'"
blob = blob[2:len(blob) - 1]
blob = base64.b64decode(blob.encode())
secret = crypt.decrypt(blob)
print(secret.decode())
