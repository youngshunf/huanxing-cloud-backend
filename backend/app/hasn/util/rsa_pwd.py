from __future__ import annotations

import base64

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def rsa_encrypt_password(plain: str, public_pem: str) -> str:
    key = serialization.load_pem_public_key(public_pem.encode("utf-8"))
    encrypted = key.encrypt(
        base64.b64encode(plain.encode("utf-8")),
        padding.PKCS1v15(),
    )
    return base64.b64encode(encrypted).decode("ascii")
