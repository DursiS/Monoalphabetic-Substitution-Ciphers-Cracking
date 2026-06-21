import time
from collections import defaultdict
from itertools import combinations
from typing import Any

import numpy as np

from Cipher_Cracking.preprocessing.Enigma.EnigmaMachine import (
    EnigmaMachine,
    EnigmaSetting,
)
from Cipher_Cracking.preprocessing.facade import CipherStarter
from collections import defaultdict


CRIBS = [
    "WETTER",
    "KEINE BESONDEREN EREIGNISSE",
    "HEIL HITLER",
    "EINS",
]

GERMAN_IOC = 0.0762


class EnigmaCracker:
    """A machine to decrypt enigma ciphers without knowing its settings
    or message key."""

    cribs: list[str]
    starter: CipherStarter
    enigma: EnigmaMachine

    def __init__(self, starter: CipherStarter, cribs: list[str]) -> None:
        self.starter = starter
        self.cribs = cribs

    def crack(self, message: str) -> str:
        """Return <message> decrypted

        No letter could map to itself
        Compare samples decryption to cribs
        """
        clean_text = self.starter.clean_text(message)
        rotor_states = self.rotor_states()
        edge_dct = self.build_edges(clean_text, self.cribs)

        candidates = []
        for alignment in list(edge_dct.keys()):
            graph = self.get_graph(alignment)
            loops = self.find_loops(graph)
            if not loops:
                continue
            for abs_state in rotor_states:
                if all(self.has_fixed_point(loop, abs_state) for loop in loops):
                    candidates.append(abs_state)

        plaintexts = []
        for candidate in candidates:
            plaintexts.append(self.decrypt_with(clean_text, candidate))
        if not plaintexts:
            return ""
        return self.best_target(plaintexts)

    def fine_loops(self, graph: defaultdict[Any, list]) -> tuple:
        """Return linked lists for every loop found in graph"""
        pass

    def has_fixed_point(self, loop: tuple, abs_state: list) -> bool:
        """Return whether loop still maps to itself when
        the machine is instantiated with abs_state."""
        pass

    def decrypt_with(self, clean_text: str, candidate: str) -> str:
        """Instantiate the machine with absolute settings <candidate>
        and type in clean_text to decrypt it."""
        pass

    def best_target(self, plaintexts: list[str], ioc_threshold=GERMAN_IOC) -> bool:
        """Return the text in <plaintexts> with lowest chi-squared
        out of those that pass ioc_threshold."""
        pass

    def build_edges(
        self, clean_text: str, cribs: list[str]
    ) -> dict[tuple[str, int], tuple[str, str, int]]:
        """Return (plain, cipher, rotor_step) edges for every valid
        crib alignment (no letter mapping to itself)."""

        def no_self_map(crib, slice_) -> bool:
            """Return whether any letter in slice_ aligns in crib."""
            return all(c != s for c, s in zip(crib, slice_))

        edges_dct = {}
        for crib in cribs:
            n = len(crib)
            slices = [clean_text[i : i + n] for i in range(len(clean_text) - n + 1)]
            no_overlap_slices = [
                slice_ for slice_ in slices if no_self_map(crib, slice_)
            ]
            if no_overlap_slices:
                for j in range(len(no_overlap_slices)):
                    offset = slices.index(no_overlap_slices[j])
                    new_edges = [
                        (crib[i], no_overlap_slices[j][i], offset + i) for i in range(n)
                    ]
                    edges_dct[(crib, offset)] = new_edges
        return edges_dct

    def get_graph(self, edges: list[tuple[str, str, int]]) -> defaultdict[Any, list]:
        """Return a graph of each letter and their mapping letters."""

        menu = defaultdict(list)
        for plain, cipher, pos in edges:
            menu[plain].append((cipher, pos))
            menu[cipher].append((plain, pos))
        return menu

    def rotor_states(self) -> list:
        """Return a list of all ((pos1, pos2, pos3), (step1, step2, step3)),"""
        rotor_pos = [0, 1, 2]
        rotor_step = [i for i in range(26)]

        result = []
        for steps in combinations(rotor_step, 3):
            for pos in combinations(rotor_pos, 3):
                result.append((pos, steps))
        return result


def _demo_settings(daily_ground=("Q", "W", "E")) -> EnigmaSetting:
    """A fixed Enigma setup for the tests: 10 plugboard pairs, rotors III-I-II."""
    return EnigmaSetting(
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
        rotary_order=(2, 0, 1),
        daily_ground=daily_ground,
    )


def rotary_alphabetic_round_trip_test() -> None:
    """Test that EnigmaMachine encrypts and can properly
    recover the text by decryption."""
    starter = CipherStarter()
    enigma = EnigmaMachine(_demo_settings())

    key = "ROX"
    print(f"message key: {key}")
    print(f"             {starter.alphabet}  (plain, for reference)")

    msg = starter.clean_text(
        "WETTERVORHERSAGE FUER DIE DEUTSCHE BUCHT "
        "KEINE BESONDEREN EREIGNISSE HEIL HITLER"
    )
    ct = enigma.encrypt(key, msg)
    print(f"\nplaintext:  {msg}")
    print(f"ciphertext: {ct}")

    # CHECK 1: decrypt(encrypt(x)) == x  (round trip with the true settings)
    back = enigma.decrypt(ct)
    print(f"\nround-trip: {back}")
    print(f"  matches cleaned plaintext? {back == msg}")

    # CHECK 2: WRONG settings (different daily ground) should NOT recover it
    wrong = EnigmaMachine(_demo_settings(daily_ground=("A", "A", "A")))
    print(f"\nwrong-setting decrypt: {wrong.decrypt(ct)}")
    print(f"  (should be gibberish, != plaintext: {wrong.decrypt(ct) != msg})")


def rotary_alphabetic_cracking_test() -> None:
    """Test that EnigmaCracker can recover the message from ciphertext and
    cribs alone, without being handed the machine settings."""
    starter = CipherStarter()
    enigma = EnigmaMachine(_demo_settings())

    key = "ROX"
    msg = starter.clean_text(
        "WETTERVORHERSAGE FUER DIE DEUTSCHE BUCHT " "KEINE BESONDEREN EREIGNISSE"
    )
    ct = enigma.encrypt(key, msg)
    print(f"plaintext:  {msg}")
    print(f"ciphertext: {ct}")
    print(f"cribs:      {CRIBS}")

    # CHECK 1: crack(encrypt(x)) == msg  (cracker only sees ciphertext + cribs)
    cracker = EnigmaCracker(starter, CRIBS)
    t0 = time.perf_counter()
    back = cracker.crack(ct)
    elapsed = time.perf_counter() - t0
    print(f"\ncracking-time: {elapsed}s")
    print(f"cracked-text:  {back}")
    print(f"  matches cleaned plaintext? {back == msg}")


def rotary_alphabetic_eliminate_self_maps_test() -> None:
    """Test that eliminate_self_maps drops candidate settings whose cribs
    overlap the text, and keeps the rest (mutating the list in place)."""
    starter = CipherStarter()
    cracker = EnigmaCracker(starter, CRIBS)
    cracker.enigma = EnigmaMachine(_demo_settings())  # the sweep needs a machine

    # CHECK 1: text with NO crib in it -> every candidate setting survives
    no_crib = "ABCDEFGHIJKLMNOPQRSTUVWX"
    kept = [
        _demo_settings(("Q", "W", "E")),
        _demo_settings(("A", "A", "A")),
        _demo_settings(("M", "N", "O")),
    ]
    before = len(kept)
    cracker.eliminate_self_maps(no_crib, kept)
    print(f"no-crib text -> kept {len(kept)}/{before} settings")
    print(f"  all kept? {len(kept) == before}")

    # CHECK 2: text containing a crib ('WETTER') -> the candidate is eliminated
    with_crib = starter.clean_text("WETTER BERICHT FUER HEUTE")
    dropped = [_demo_settings()]
    before = len(dropped)
    cracker.eliminate_self_maps(with_crib, dropped)
    print(f"crib text    -> kept {len(dropped)}/{before} settings")
    print(f"  eliminated? {len(dropped) == 0}")


if __name__ == "__main__":
    rotary_alphabetic_round_trip_test()
    print()
    rotary_alphabetic_cracking_test()
    print()
    rotary_alphabetic_eliminate_self_maps_test()
