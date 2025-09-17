# helpers.py

from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.fernet import Fernet
from flask import session
from datetime import datetime
from zoneinfo import ZoneInfo

class Password:
    def set_password(self, password):
        self.password = generate_password_hash(password)
        return self.password

    def check_password(self, hashed_password, plain_password):
        return check_password_hash(hashed_password, plain_password)
#
# class APIKeyHandler:
#     def __init__(self, fernet_key):
#         self.fernet_key = fernet_key
#         self.cipher = Fernet(self.fernet_key)
#
#     def encrypt_key(self, key):
#         return self.cipher.encrypt(key.encode()).decode()
#
#     def decrypt_key(self, encrypted_key):
#         return self.cipher.decrypt(encrypted_key.encode()).decode()


def current_local_time():
    sri_lanka_tz = ZoneInfo("Asia/Colombo")
    local_time = datetime.now(sri_lanka_tz)
    return local_time