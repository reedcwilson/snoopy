#!/usr/bin/env python

from Crypto.Cipher import AES
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
