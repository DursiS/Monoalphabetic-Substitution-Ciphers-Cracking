CRIBS = [
    "WETTER",
    "KEINE BESONDEREN EREIGNISSE",
    "HEIL HITLER",
    "EINS",
]


class RotaryCracker:
    """A machine to decrypt enigma ciphers without knowing its settings
    or message key."""

    cribs: list[str]

    def decrypt(self, message: str) -> str:
        """Return <message> decrypted.

        No letter could map to itself
        Compare samples decryption to cribs
        """

    def get_plugboard(self) -> dict[str, str]:
        """Because of the reflector's reciprocity,
        the plugboard settings cancel out around a complete loop."""
        for char in ALPHABET:
