from Crypto.Cipher import AES as AES_ENCRYPTION
from Crypto.Random import get_random_bytes
from typing_extensions import Self


class AES:
    def __init__(self, key: bytes | None = None) -> None:
        self.key: bytes = key or self.generate_key()

    @classmethod
    def from_hex(cls, key: str) -> Self:
        return cls(bytes.fromhex(key))

    def generate_key(self, key_size: int = 32) -> bytes:
        return get_random_bytes(key_size)

    def generate_nonce(self, nonce_size: int = 12) -> bytes:
        return get_random_bytes(nonce_size)

    def export_key(self) -> str:
        return self.key.hex()

    def encrypt(self, data: bytes, nonce: bytes | None = None) -> bytes:
        nonce = nonce or self.generate_nonce()
        cipher = AES_ENCRYPTION.new(self.key, AES_ENCRYPTION.MODE_GCM, nonce=nonce)
        ciphertext, tag = cipher.encrypt_and_digest(data)
        return nonce + ciphertext + tag

    def decrypt(self, data: bytes) -> bytes:
        nonce, ciphertext, tag = (
            data[:12],
            data[12:-16],
            data[-16:],
        )
        cipher = AES_ENCRYPTION.new(self.key, AES_ENCRYPTION.MODE_GCM, nonce=nonce)
        return cipher.decrypt_and_verify(ciphertext, tag)
