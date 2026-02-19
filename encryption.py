"""Encryption module for Smart-Encrypt"""
import os
import hashlib
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
import base64

PBKDF2_ITERATIONS = 200000

class EncryptionManager:
    def __init__(self):
        self.fernet = None
        self.salt = None
    
    def derive_key(self, password: str, salt: bytes = None) -> bytes:
        if salt is None:
            salt = secrets.token_bytes(32)
        self.salt = salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=PBKDF2_ITERATIONS,
        )
        return base64.urlsafe_b64encode(kdf.derive(password.encode()))
    
    def initialize(self, password: str, salt: bytes = None):
        key = self.derive_key(password, salt)
        self.fernet = Fernet(key)
    
    def encrypt(self, data: str) -> bytes:
        if not self.fernet:
            raise ValueError("Encryption not initialized")
        return self.fernet.encrypt(data.encode())
    
    def decrypt(self, encrypted_data: bytes) -> str:
        if not self.fernet:
            raise ValueError("Encryption not initialized")
        return self.fernet.decrypt(encrypted_data).decode()
    
    def hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(32)
        pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ITERATIONS)
        return base64.b64encode(salt + pwdhash).decode()
    
    def verify_password(self, password: str, stored_hash: str) -> bool:
        try:
            decoded = base64.b64decode(stored_hash.encode())
            salt = decoded[:32]
            stored_pwdhash = decoded[32:]
            pwdhash = hashlib.pbkdf2_hmac('sha256', password.encode(), salt, PBKDF2_ITERATIONS)
            return secrets.compare_digest(stored_pwdhash, pwdhash)
        except:
            return False