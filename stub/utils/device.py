import os
import uuid
import json
import socket
import getpass
import hashlib
import platform
import requests
import subprocess
from dataclasses import dataclass
from stub.utils import Serializable
from typing import TypeAlias, List, Dict, Any

__all__ = ["DeviceInfo"]
MaybeStr: TypeAlias = str | None


@dataclass
class DeviceInfo(Serializable):
    hostname: MaybeStr = None
    local_ip_address: MaybeStr = None
    public_ip_address: MaybeStr = None
    mac_address: MaybeStr = None
    os: MaybeStr = None
    platform: MaybeStr = None
    version: MaybeStr = None
    release: MaybeStr = None
    hwid: MaybeStr = None
    disk_num: MaybeStr = None

    @staticmethod
    def get_hwid() -> str:
        cmd = subprocess.Popen(
            "wmic useraccount where name='%username%' get sid",
            stdout=subprocess.PIPE,
            shell=True,
        )
        suppost_sid, _ = cmd.communicate()
        return suppost_sid.split(b"\n")[1].strip().decode("utf-8")

    @staticmethod
    def get_disk_num():
        cmd = subprocess.Popen(
            """wmic diskdrive get serialnumber""",
            stdout=subprocess.PIPE,
            shell=True,
        )
        suppost_sid, _ = cmd.communicate()
        return suppost_sid.split(b"\n")[1].strip().decode("utf-8")

    def __post_init__(self) -> None:
        self.hostname = getpass.getuser()
        self.local_ip_address = socket.gethostbyname(socket.gethostname())
        self.mac_address = ":".join(
            ["{:02x}".format((uuid.getnode() >> ele) & 0xFF) for ele in range(0, 48, 8)]
        )
        self.os = os.name
        self.hwid = self.get_hwid()
        self.disk_num = self.get_disk_num()

        _info = platform.uname()
        self.platform = _info.system
        self.version = _info.version
        self.release = _info.release

        self.public_ip_address = requests.get("https://api.ipify.org").content.decode(
            "utf8"
        )

    def hashes(self) -> List[str]:
        """
        Returns multiples hashes of the device info.
        """
        to_hash: List[Dict[str, Any]] = []
        hashed: List[str] = []

        payload = self.to_dict()
        to_hash.extend(
            [
                payload,
                payload["hwid"],
                payload["mac_address"],
                payload["disk_num"],
                payload["public_ip_address"],
            ]
        )

        for p in to_hash:
            hashed.append(
                hashlib.md5(json.dumps(p, sort_keys=True).encode("utf-8")).hexdigest()
            )

        return hashed
