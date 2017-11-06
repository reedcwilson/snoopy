#!/usr/bin/env python

from Crypto.Cipher import AES
import getpass
import os
import base64
import struct


def pad16(s):
    t = struct.pack('>I', len(s)) + s.encode()
    return t + b'\x00' * ((16 - len(t) % 16) % 16)


def unpad16(s):
    n = struct.unpack('>I', s[:4])[0]
    return s[4:n + 4]


class Crypt(object):
    def __init__(self, password):
        password = pad16(password)
        self.cipher = AES.new(password, AES.MODE_ECB)

    def encrypt(self, s):
        s = pad16(s)
        return self.cipher.encrypt(s)

    def decrypt(self, s):
        t = self.cipher.decrypt(s)
        return unpad16(t)


class SecretsManager():
    def __init__(self, key, filename):
        self.filename = filename
        self.crypt = Crypt(key)

    def get(self):
        with open(self.filename, 'rb') as f:
            return self.crypt.decrypt(f.read()).decode()

    def put(self, secrets):
        with open(self.filename, 'wb') as f:
            f.write(self.crypt.encrypt(secrets))

    def encrypt(self, secret):
        return self.crypt.encrypt(secret)

    def decrypt(self, secret):
        return self.crypt.decrypt(secret)


def helper(password):
    crypt = Crypt(password)
    kind = input('would you like to "e"ncrypt or ["d"ecrypt]: ')
    value = None
    if kind.lower() == 'e':
        secret = getpass.getpass("what is the secret: ")
        value = crypt.encrypt(secret)
        value = base64.b64encode(value).decode()
    else:
        blob = input("what is the ciphertext: ")
        text = base64.b64decode(blob.encode())
        value = crypt.decrypt(text).decode()
    os.system('echo "{}\c" | pbcopy'.format(value))


def decrypt_config(password):
    filename = input("what is the filename: ")
    mgr = SecretsManager(password, filename)
    print(mgr.get())


def encrypt_config(password):
    filename = input("what is the filename: ")
    mgr = SecretsManager(password, filename)
    text = '''
    put text here
    '''
    print(mgr.put(text))


if __name__ == '__main__':
    password = getpass.getpass("what is the password: ")
    helper(password)
    # decrypt_config(password)
    # encrypt_config(password)
