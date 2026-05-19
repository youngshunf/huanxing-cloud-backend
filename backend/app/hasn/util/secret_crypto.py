from __future__ import annotations

from backend.app.llm.core.encryption import key_encryption


def encrypt_ragflow_secret(plaintext: str) -> bytes:
    if plaintext == "":
        return b""
    return key_encryption.encrypt(plaintext).encode("utf-8")


def decrypt_ragflow_secret(ciphertext: bytes | str | None) -> str:
    if ciphertext in (None, b"", ""):
        return ""
    encoded = ciphertext.decode("utf-8") if isinstance(ciphertext, bytes) else ciphertext
    try:
        return key_encryption.decrypt(encoded)
    except Exception:
        return encoded
