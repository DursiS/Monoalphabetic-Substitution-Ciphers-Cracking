import string
from dataclasses import dataclass

from Enigma.reflector import (
    REFLECTOR_B,
    ROTOR_0,
    ROTOR_0_INV,
    ROTOR_1,
    ROTOR_1_INV,
    ROTOR_2,
    ROTOR_2_INV,
)
from Enigma.sample_messages import MESSAGES


ALPHABET = string.ascii_uppercase
ROTORS = [ROTOR_0, ROTOR_1, ROTOR_2]
ROTORS_INV = [ROTOR_0_INV, ROTOR_1_INV, ROTOR_2_INV]


class Rotary:
    """A rotary representing a cipher in Enigma,"""

    notch: int
    inwards: dict[str, str]
    outwards: dict[str, str]
    num: int
    order_pos: int
    pos: int
    original_pos: int

    def __init__(self, num: int, pos: int, start_char: str) -> None:
        self.num = num
        self.order_pos = pos
        self.inwards = ROTORS[num]
        self.outwards = ROTORS_INV[num]
        self.setStart(start_char)
        self.pos = ALPHABET.index(start_char)
        self.original_pos = ALPHABET.index(start_char)

        if self.num == 0:
            self.notch = ALPHABET.index("Q")
        elif self.num == 1:
            self.notch = ALPHABET.index("E")
        else:
            self.notch = ALPHABET.index("V")

    def map(
        self, char: str, contact: int, should_rotate: bool, inwards: bool = True
    ) -> tuple[str, int, bool]:
        """Return the mapping of whatever absolute position
        this rotor is on, and the absolute position which it comes out of."""
        rotate_next = False
        if inwards and (self.order_pos == 2 or should_rotate):
            self.rotate()
        if self.notch == self.pos:
            rotate_next = True

        entry = (ALPHABET.index(char) + self.pos) % 26
        if inwards:
            mapped = self.inwards[ALPHABET[entry]]
        else:
            mapped = self.outwards[ALPHABET[entry]]
        exit = (ALPHABET.index(mapped) - self.pos) % 26
        return ALPHABET[exit], exit, rotate_next

    def route(self, char: str, inwards: bool = True) -> str:
        """Map <char> through the rotor at its CURRENT position with no stepping.
        inwards uses the forward wiring; outwards the inverse (the return leg)."""
        entry = (ALPHABET.index(char) + self.pos) % 26
        table = self.inwards if inwards else self.outwards
        mapped = table[ALPHABET[entry]]
        return ALPHABET[(ALPHABET.index(mapped) - self.pos) % 26]

    def rotate(self) -> None:
        """Rotate this rotary mapping clockwise."""
        self.pos = (self.pos + 1) % 26

    def setStart(self, char: str) -> None:
        """Set the starting <char> by rotating the rotary."""
        self.pos = ALPHABET.index(char)


@dataclass
class EnigmaSetting:
    """Settings for enigma."""

    plugboard: dict[str, str]
    rotary_start: tuple[str, str, str]
    rotary_order: tuple[int, int, int]
    daily_ground: tuple[str, str, str]


class EnigmaMachine:
    """A digital imitation of a WWII Enigma Machine."""

    settings: EnigmaSetting
    rotaries: tuple[Rotary, ...]
    reflector: dict[str, str]

    def __init__(self, settings: EnigmaSetting) -> None:
        self.set_settings(settings)

    def set_settings(self, settings: EnigmaSetting) -> None:
        """Configure (or reconfigure) the machine from <settings>: rebuild the
        rotors at their daily-ground positions and fit the reflector."""
        self.settings = settings
        self.reflector = REFLECTOR_B
        self.set_rotor_state((settings.rotary_order, settings.daily_ground))

    def set_rotor_state(
        self,
        rotor_state: tuple[tuple[int, int, int], tuple[str, str, str]],
    ) -> None:
        """Set only the rotor state. <rotor_state> is (rotary_order, rotary_start):
        rotary_order is which wiring sits in each slot (left to right) and
        rotary_start their absolute starting positions. Plugboard and reflector
        are left untouched."""
        rotary_order, rotary_start = rotor_state
        self.rotaries = tuple(
            Rotary(rotary_order[i], i, rotary_start[i]) for i in range(3)
        )

    def set_plugboard(self, wires: list[tuple[str, str]]) -> None:
        """Replace the plugboard with the symmetric mapping built from <wires>."""
        plugboard: dict[str, str] = {}
        for a, b in wires:
            plugboard[a] = b
            plugboard[b] = a
        self.settings.plugboard = plugboard

    def scramble(self, char: str) -> str:
        """The plugboard-free scrambler at the current rotor positions: forward
        through the rotors, reflect, back through the rotors -- no stepping, no
        plugboard. An involution with no fixed points (one bombe drum)."""
        for i in (2, 1, 0):  # right -> left, toward the reflector
            char = self.rotaries[i].route(char, inwards=True)
        char = self.reflector[char]
        for i in (0, 1, 2):  # left -> right, back out
            char = self.rotaries[i].route(char, inwards=False)
        return char

    def scramblers_for(
        self,
        rotor_state: tuple[tuple[int, int, int], tuple[str, str, str]],
        positions,
    ) -> dict[int, dict[str, str]]:
        """Return {pos: permutation} of the plugboard-free scrambler at each menu
        offset in <positions>, built in one forward pass from <rotor_state>. The
        rotors are stepped exactly as the machine encrypts (step then scramble),
        so offset k lines up with how decrypt_with treats index k."""
        wanted = set(positions)
        if not wanted:
            return {}
        self.set_rotor_state(rotor_state)
        result = {}
        for k in range(max(wanted) + 1):
            self.press("A")  # advance the rotors as the machine would; output discarded
            if k in wanted:
                result[k] = {ch: self.scramble(ch) for ch in ALPHABET}
        return result

    def press(self, char: str) -> str:
        """Press <char> on the keyboard and return what is
        seen on the lightboard."""
        if char in self.settings.plugboard:
            char = self.settings.plugboard[char]

        contact = self.rotaries[2].pos
        rotate_next = self.rotaries[2].pos == self.rotaries[2].notch
        for i in range(2, -1, -1):
            if i == 0:
                rotate_next = self.rotaries[0].pos == self.rotaries[0].notch
                char, contact, rotate_next = self.rotaries[i].map(
                    char, self.rotaries[i].pos, rotate_next, True
                )
            else:
                char, contact, rotate_next = self.rotaries[i].map(
                    char, contact, rotate_next, True
                )

        char = self.reflector[char]

        for i in range(3):
            if i == 0:
                char, contact, rotate_next = self.rotaries[i].map(
                    char, self.rotaries[i].pos, rotate_next, False
                )
            else:
                char, contact, rotate_next = self.rotaries[i].map(
                    char, contact, rotate_next, False
                )

        if char in self.settings.plugboard:
            char = self.settings.plugboard[char]

        return char

    def encrypt(self, key: str, text: str) -> str:
        """Encrypt <text> through enigma given <key>."""
        indicator = self.get_indicator(key)
        self.setRotors(key)
        result = "".join(self.press(char) for char in text)
        return indicator + result

    def decrypt(self, text: str) -> str:
        """Decrypt <text> through enigma."""
        self.setRotors("".join(char for char in self.settings.daily_ground))
        body = text[6:]
        indicator = text[:6]

        recovered_key = "".join(self.press(char) for char in indicator[:3])
        self.setRotors(recovered_key)
        return "".join(self.press(char) for char in body)

    def get_indicator(self, message_key: str) -> str:
        """Return the 6 letter indicator as <key> typed twice."""
        return "".join(self.press(char) for char in message_key * 2)

    def setRotors(self, message_key: str) -> None:
        """Set the starting positions of the rotaries
        according to <indicator>."""
        for i in range(3):
            self.rotaries[i].setStart(message_key[i])


def clean_text(text):
    """Strip to uppercase A-Z only (drop spaces, punctuation, digits).
    Classic substitution works on the bare letter stream."""
    return "".join(ch for ch in text.upper() if ch in ALPHABET)


if __name__ == "__main__":
    settings = EnigmaSetting(
        plugboard={
            "A": "M",
            "M": "A",
            "F": "I",
            "I": "F",
            "N": "V",
            "V": "N",
            "P": "S",
            "S": "P",
            "T": "U",
            "U": "T",
            "W": "Z",
            "Z": "W",
            "B": "G",
            "G": "B",
            "H": "K",
            "K": "H",
            "D": "X",
            "X": "D",
            "C": "Q",
            "Q": "C",
        },
        rotary_start=("A", "B", "L"),
        rotary_order=(
            2,
            0,
            1,
        ),
        daily_ground=("Q", "W", "E"),
    )
    enigma = EnigmaMachine(settings)

    key = "ROX"
    sample_text = clean_text(MESSAGES[0]["text"])
    encrypted = enigma.encrypt(key, sample_text)
    decrypted = enigma.decrypt(encrypted)

    print(f"Initial:\n{sample_text}\n")
    print(f"Encrypted:\n{encrypted}\n")
    print(f"Decrypted:\n{decrypted}\n")
