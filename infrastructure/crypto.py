"""
محرك التشفير المتقدم - دعم التوقيع (Ed25519, RSA-PSS)، وتشفير المفتاح الخاص
"""

import hashlib
import base64
import os
import json
from typing import Tuple, Optional, Union
from pathlib import Path

try:
    from Cryptodome.Cipher import AES, ChaCha20_Poly1305
    from Cryptodome.PublicKey import RSA
    try:
        from Cryptodome.PublicKey import Ed25519
        HAS_ED25519 = True
    except Exception:
        HAS_ED25519 = False
    from Cryptodome.Random import get_random_bytes
    from Cryptodome.Protocol.KDF import scrypt, PBKDF2
    from Cryptodome.Util.Padding import pad, unpad
    from Cryptodome.Signature import pss
    from Cryptodome.Hash import SHA512
    from Cryptodome.Signature import eddsa
    HAS_CRYPTODOME = True
except ImportError:
    HAS_CRYPTODOME = False
    HAS_ED25519 = False

from infrastructure.logger import app_logger


class CryptoEngine:
    """
    محرك التشفير المتقدم مع دعم لتوليد المفاتيح والتوقيع.
    """

    @staticmethod
    def derive_key_scrypt(password: str, salt: bytes, key_length: int = 32) -> bytes:
        try:
            return scrypt(password.encode(), salt, key_length, N=2 ** 14, r=8, p=1)
        except Exception as e:
            app_logger.error(f"Key derivation failed: {e}")
            raise

    @staticmethod
    def derive_key_pbkdf2(password: str, salt: bytes, key_length: int = 32) -> bytes:
        return PBKDF2(password.encode(), salt, dkLen=key_length, count=100000)

    # ===== AES-GCM helpers for encrypting private keys =====
    @staticmethod
    def encrypt_private_key(private_pem: bytes, sym_key: bytes) -> bytes:
        """Encrypt private PEM bytes using AES-GCM with a derived 32-byte key.
        Format: nonce(12) + tag(16) + ciphertext
        """
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            key = hashlib.sha256(sym_key).digest()
            nonce = get_random_bytes(12)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            ct, tag = cipher.encrypt_and_digest(private_pem)
            return nonce + tag + ct
        except Exception as e:
            app_logger.error(f"encrypt_private_key failed: {e}")
            raise

    @staticmethod
    def decrypt_private_key(enc_blob: bytes, sym_key: bytes) -> bytes:
        """Decrypt private key produced by encrypt_private_key
        Expects: nonce(12) + tag(16) + ciphertext
        Returns private_pem bytes
        """
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            if len(enc_blob) < 28:
                raise ValueError("Invalid encrypted blob")
            key = hashlib.sha256(sym_key).digest()
            nonce = enc_blob[:12]
            tag = enc_blob[12:28]
            ct = enc_blob[28:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ct, tag)
        except Exception as e:
            app_logger.error(f"decrypt_private_key failed: {e}")
            raise

    # ===== Ed25519 =====
    @staticmethod
    def generate_ed25519_keypair() -> Tuple[bytes, bytes]:
        if not HAS_CRYPTODOME or not HAS_ED25519:
            raise ImportError("Ed25519 not available in pycryptodome")
        try:
            key = Ed25519.generate()
            private_pem = key.export_key(format='PEM')
            public_pem = key.public_key().export_key(format='PEM')
            return public_pem, private_pem
        except Exception as e:
            app_logger.error(f"generate_ed25519_keypair failed: {e}")
            raise

    @staticmethod
    def sign_with_ed25519(data: bytes, private_pem: bytes) -> bytes:
        if not HAS_CRYPTODOME or not HAS_ED25519:
            raise ImportError("Ed25519 not available in pycryptodome")
        try:
            key = Ed25519.import_key(private_pem)
            signer = eddsa.new(key=key, mode='rfc8032')
            sig = signer.sign(data)
            return sig
        except Exception as e:
            app_logger.error(f"sign_with_ed25519 failed: {e}")
            raise

    @staticmethod
    def verify_ed25519(data: bytes, signature: bytes, public_pem: bytes) -> bool:
        if not HAS_CRYPTODOME or not HAS_ED25519:
            raise ImportError("Ed25519 not available in pycryptodome")
        try:
            key = Ed25519.import_key(public_pem)
            verifier = eddsa.new(key=key, mode='rfc8032')
            verifier.verify(data, signature)
            return True
        except Exception as e:
            app_logger.error(f"verify_ed25519 failed: {e}")
            return False

    # ===== RSA-PSS =====
    @staticmethod
    def generate_rsa_keypair(key_size: int = 4096) -> Tuple[bytes, bytes]:
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            key = RSA.generate(key_size)
            private_pem = key.export_key(format='PEM')
            public_pem = key.publickey().export_key(format='PEM')
            return public_pem, private_pem
        except Exception as e:
            app_logger.error(f"generate_rsa_keypair failed: {e}")
            raise

    @staticmethod
    def sign_with_rsa_pss(data: bytes, private_pem: bytes) -> bytes:
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            key = RSA.import_key(private_pem)
            h = SHA512.new(data)
            signature = pss.new(key).sign(h)
            return signature
        except Exception as e:
            app_logger.error(f"sign_with_rsa_pss failed: {e}")
            raise

    @staticmethod
    def verify_rsa_pss(data: bytes, signature: bytes, public_pem: bytes) -> bool:
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            key = RSA.import_key(public_pem)
            h = SHA512.new(data)
            pss.new(key).verify(h, signature)
            return True
        except Exception as e:
            app_logger.error(f"verify_rsa_pss failed: {e}")
            return False

    # ===== Generic helpers =====
    @staticmethod
    def sha256(data: bytes) -> str:
        return hashlib.sha256(data).hexdigest()

    @staticmethod
    def base64_encode(data: bytes) -> str:
        return base64.b64encode(data).decode('utf-8')

    @staticmethod
    def base64_decode(data: str) -> bytes:
        return base64.b64decode(data)

    # legacy simple AES helpers (kept for backward compatibility)
    @staticmethod
    def aes_encrypt(data: bytes, key: bytes) -> bytes:
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            nonce = get_random_bytes(12)
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            ciphertext, tag = cipher.encrypt_and_digest(data)
            return nonce + tag + ciphertext
        except Exception as e:
            app_logger.error(f"AES encryption failed: {e}")
            raise

    @staticmethod
    def aes_decrypt(encrypted: bytes, key: bytes) -> bytes:
        if not HAS_CRYPTODOME:
            raise ImportError("pycryptodome not installed")
        try:
            if len(encrypted) < 28:
                raise ValueError("Invalid encrypted data")
            nonce = encrypted[:12]
            tag = encrypted[12:28]
            ciphertext = encrypted[28:]
            cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
            return cipher.decrypt_and_verify(ciphertext, tag)
        except Exception as e:
            app_logger.error(f"AES decryption failed: {e}")
            raise

    # keep other crypto methods from original file as needed (xor, hashes)
    @staticmethod
    def xor_advanced(data: bytes, key: bytes) -> bytes:
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
        try:
            result = data
            for key in keys:
                result = CryptoEngine.xor_advanced(result, key)
            return result
        except Exception as e:
            app_logger.error(f"Multi-XOR encryption failed: {e}")
            raise

    @staticmethod
    def md5(data: bytes) -> str:
        return hashlib.md5(data).hexdigest()
