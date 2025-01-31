from Cryptodome.Cipher import PKCS1_OAEP
from Cryptodome.PublicKey import RSA as RSA_ENCRYPTION
from Cryptodome.Hash import SHA256
from typing_extensions import Self
from typing import Tuple
import base64


class RSA:
    def __init__(
        self,
        key_size: int = 4096,
        pub_key: RSA_ENCRYPTION.RsaKey | None = None,
        priv_key: RSA_ENCRYPTION.RsaKey | None = None,
    ) -> None:
        if pub_key:
            self.public_key = pub_key
        else:
            self.public_key = (
                priv_key.publickey() if priv_key else self.generate_key_pair(key_size)
            )

        self.private_key = priv_key

    @classmethod
    def from_keys(
        cls, private_key_pem: str | None = None, public_key_pem: str | None = None
    ) -> Self:
        private_key = (
            RSA_ENCRYPTION.import_key(private_key_pem.encode("utf-8"))
            if private_key_pem
            else None
        )
        public_key = (
            RSA_ENCRYPTION.import_key(public_key_pem.encode("utf-8"))
            if public_key_pem
            else None
        )
        return cls(priv_key=private_key, pub_key=public_key)

    @staticmethod
    def generate_key_pair(key_size: int) -> RSA_ENCRYPTION.RsaKey:
        return RSA_ENCRYPTION.generate(key_size)

    def export_keys(self) -> Tuple[str | None, str | None]:
        private_key_pem = (
            self.private_key.export_key().decode("utf-8") if self.private_key else None
        )
        public_key_pem = self.public_key.export_key().decode("utf-8")
        return private_key_pem, public_key_pem

    def encrypt(
        self,
        data: bytes,
    ) -> str:
        cipher = PKCS1_OAEP.new(self.public_key, hashAlgo=SHA256)
        encrypted_data = cipher.encrypt(data)
        return base64.b64encode(encrypted_data).decode("utf-8")

    def decrypt(self, data: str) -> bytes:
        assert self.private_key is not None
        cipher = PKCS1_OAEP.new(self.private_key, hashAlgo=SHA256)
        decoded_data = base64.b64decode(data)
        return cipher.decrypt(decoded_data)
