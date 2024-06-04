import base64
import hashlib

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

from config import SECRET


def crypt_message_with_aes(message: str):
    message_byte = message.encode('utf-8')
    cipher = AES.new(key=hashlib.sha256(SECRET.encode('utf-8')).digest(), mode=AES.MODE_ECB)
    crypted = cipher.encrypt(pad(message_byte, AES.block_size))
    return base64.b85encode(crypted).decode('utf-8')


__all__ = ['crypt_message_with_aes']
