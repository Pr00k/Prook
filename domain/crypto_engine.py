"""
محرك العمليات المشفرة (واجهة مبسطة)
"""

from infrastructure.crypto import CryptoEngine as CoreCrypto


class CryptoEngine:
    """واجهة مبسطة للتشفير"""
    
    @staticmethod
    def encrypt(data: bytes, key: bytes) -> bytes:
        return CoreCrypto.aes_encrypt(data, key)
    
    @staticmethod
    def decrypt(data: bytes, key: bytes) -> bytes:
        return CoreCrypto.aes_decrypt(data, key)
    
    @staticmethod
    def hash(data: bytes) -> str:
        return CoreCrypto.sha256(data)
    
    @staticmethod
    def encode_base64(data: bytes) -> str:
        return CoreCrypto.base64_encode(data)
    
    @staticmethod
    def decode_base64(data: str) -> bytes:
        return CoreCrypto.base64_decode(data)