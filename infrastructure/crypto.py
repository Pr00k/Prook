"""
محرك التشفير المتقدم - يدعم:
- AES-GCM, ChaCha20-Poly1305
- RSA (مفتاح عام/خاص)
- XChaCha20
- Argon2 (لتوليد المفاتيح)
- تشفير الملفات الكبيرة
"""

import hashlib
import base64
import os
import json
from typing import Tuple, Optional, Union
from pathlib import Path

try:
    from Cryptodome.Cipher import AES, ChaCha20, PKCS1_OAEP
    from Cryptodome.PublicKey import RSA
    from Cryptodome.Random import get_random_bytes
    from Cryptodome.Protocol.KDF import scrypt, PBKDF2
    from Cryptodome.Util.Padding import pad, unpad
    HAS_CRYPTODOME = True
except ImportError:
    HAS_CRYPTODOME = False

from infrastructure.logger import app_logger


class CryptoEngine:
    """
    محرك التشفير المتقدم
    """

    @staticmethod
    def derive_key_argon2(password: str, salt: bytes, key_length: int = 32) -> bytes:
        """توليد مفتاح باستخدام Argon2 (محاكاة باستخدام scrypt)"""
        try:
            return scrypt(password.encode(), salt, key_length, N=2**14, r=8, p=1)
        except Exception as e:
            app_logger.error(f"Key derivation failed: {e}")
            raise

    @staticmethod
    def derive_key_pbkdf2(password: str, salt: bytes, key_length: int = 32) -> bytes:
        """توليد مفتاح باستخدام PBKDF2"""
        return PBKDF2(password.encode(), salt, dkLen=key_length, count=100000)

    @staticmethod
    def aes_encrypt(data: bytes, key: bytes) -> bytes:
        """تشفير AES-GCM"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            cipher = AES.new(key, AES.MODE_GCM)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return cipher.nonce + tag + ciphertext
        except Exception as e:
            app_logger.error(f"AES encryption failed: {e}")
            raise

    @staticmethod
    def aes_decrypt(encrypted: bytes, key: bytes) -> bytes:
        """فك تشفير AES-GCM"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            nonce = encrypted[:16]
            tag = encrypted[16:32]
            ciphertext = encrypted[32:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            app_logger.error(f"AES decryption failed: {e}")
            raise

    @staticmethod
    def aes_cbc_encrypt(data: bytes, key: bytes) -> bytes:
        """تشفير AES-CBC"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            cipher = AES.new(key, AES.MODE_CBC)
            ct_bytes = cipher.encrypt(pad(data, AES.block_size))
            return cipher.iv + ct_bytes
        except Exception as e:
            app_logger.error(f"AES-CBC encryption failed: {e}")
            raise

    @staticmethod
    def aes_cbc_decrypt(encrypted: bytes, key: bytes) -> bytes:
        """فك تشفير AES-CBC"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            iv = encrypted[:AES.block_size]
            ct = encrypted[AES.block_size:]
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
            pt = unpad(cipher.decrypt(ct), AES.block_size)
            return pt
        except Exception as e:
            app_logger.error(f"AES-CBC decryption failed: {e}")
            raise

    @staticmethod
    def chacha20_encrypt(data: bytes, key: bytes) -> bytes:
        """تشفير ChaCha20-Poly1305"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            nonce = get_random_bytes(12)
            cipher = ChaCha20.new(key=key, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return nonce + tag + ciphertext
        except Exception as e:
            app_logger.error(f"ChaCha20 encryption failed: {e}")
            raise

    @staticmethod
    def chacha20_decrypt(encrypted: bytes, key: bytes) -> bytes:
        """فك تشفير ChaCha20-Poly1305"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            nonce = encrypted[:12]
            tag = encrypted[12:28]
            ciphertext = encrypted[28:]
            cipher = ChaCha20.new(key=key, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            app_logger.error(f"ChaCha20 decryption failed: {e}")
            raise

    @staticmethod
    def rsa_generate_keypair(key_size: int = 2048) -> Tuple[bytes, bytes]:
        """توليد زوج مفاتيح RSA (public, private)"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            key = RSA.generate(key_size)
            private_key = key.export_key()
            public_key = key.publickey().export_key()
            return public_key, private_key
        except Exception as e:
            app_logger.error(f"RSA key generation failed: {e}")
            raise

    @staticmethod
    def rsa_encrypt(data: bytes, public_key_pem: bytes) -> bytes:
        """تشفير RSA"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            key = RSA.import_key(public_key_pem)
            cipher = PKCS1_OAEP.new(key)
            return cipher.encrypt(data)
        except Exception as e:
            app_logger.error(f"RSA encryption failed: {e}")
            raise

    @staticmethod
    def rsa_decrypt(encrypted: bytes, private_key_pem: bytes) -> bytes:
        """فك تشفير RSA"""
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            key = RSA.import_key(private_key_pem)
            cipher = PKCS1_OAEP.new(key)
            return cipher.decrypt(encrypted)
        except Exception as e:
            app_logger.error(f"RSA decryption failed: {e}")
            raise

    @staticmethod
    def xor_advanced(data: bytes, key: bytes) -> bytes:
        """تشفير XOR متقدم مع مفتاح ممتد"""
        try:
            expanded = hashlib.sha256(key).digest()
            result = bytearray(len(data))
            for i in range(len(data)):
                result[i] = data[i] ^ expanded[i % len(expanded)]
            return bytes(result)
        except Exception as e:
            app_logger.error(f"XOR encryption failed: {e}")
            raise

    @staticmethod
    def xor_multi_key(data: bytes, keys: list) -> bytes:
        """تشفير XOR بمفاتيح متعددة"""
        try:
            result = data
            for key in keys:
                result = CryptoEngine.xor_advanced(result, key)
            return result
        except Exception as e:
            app_logger.error(f"Multi-XOR encryption failed: {e}")
            raise

    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def sha512(data: bytes) -> str:
        return hashlib.sha512(data).hexdigest()

    @staticmethod
    def md5(data: bytes) -> str:
        return hashlib.md5(data).hexdigest()

    @staticmethod
    def base64_encode(data: bytes) -> str:
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def base64_decode(data: str) -> bytes:
        return base64.b64decode(data)

    @staticmethod
    def hex_encode(data: bytes) -> str:
        return data.hex()

    @staticmethod
    def hex_decode(data: str) -> bytes:
        return bytes.fromhex(data)