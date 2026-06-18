import os

from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.ciphers.aead import AESGCM  # or ChaCha20Poly1305
import os, base64


class ModernTextCipher:
    """An engine to encrypt and decrypt english text."""

    def __init__(self, key: str = None) -> None:
        self.key = key.encode() if key else Fernet.generate_key()
        self._auth = Fernet(self.key)

    def encrypt(self, raw_text: str) -> str:
        """Encode <raw_text> using the native encryption, then str with
        base64."""
        return self._auth.encrypt(raw_text.encode()).decode("ascii")

    def decrypt(self, token: str) -> str:
        """Decode <token> using the native encryption, then back from base64."""
        return self._auth.decrypt(token.encode()).decode()
