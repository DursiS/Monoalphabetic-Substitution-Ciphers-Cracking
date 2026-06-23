import time
from collections import defaultdict
from itertools import permutations, product
from typing import Any, Counter

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

    def __init__(
        self, starter: CipherStarter, cribs: list[str], enigma: EnigmaMachine
    ) -> None:
        self.starter = starter
        self.cribs = cribs
        self.enigma = enigma

    def crack(self, message: str) -> str:
        """Return <message> decrypted"""
        clean_text = self.starter.clean_text(message)
        rotor_states = self.rotor_states()
        edges_dict = self.build_edges(clean_text, self.cribs)

        candidates = []
        for alignment in list(edges_dict.keys()):
            edges = edges_dict[alignment]
            graph = self.get_graph(edges)
            loops = self.find_loops(graph)

            if not loops:
                continue
            for abs_state in rotor_states:
                plugboard = self.get_plugboard(loops, abs_state)
                self.enigma.set_plugboard(plugboard)
                if all(self.has_fixed_point(loop, abs_state) for loop in loops):
                    candidates.append(abs_state)

        plaintexts = []
        for candidate in candidates:
            plaintexts.append(self.decrypt_with(clean_text, candidate))
        if not plaintexts:
            return ""
        return self.best_target(plaintexts)

    def char_loops(
        self, graph: defaultdict[Any, list], start: str
    ) -> list[list[tuple[str, str, int]]]:
        """Return every simple loop through <start>, each as a list of
        positioned edges [(from, to, pos), ...] that chains back to <start>.

        Detection is a depth-first walk that never revisits a letter (except to
        close at <start>) and never reuses the same physical edge -- an edge is
        keyed by (frozenset({a, b}), pos), so two edges between the same letters
        at different offsets still count as a genuine two-step loop.
        """
        result: list[list[tuple[str, str, int]]] = []

        def dfs(node, visited, used_edges, path):
            for neighbor, pos in graph.get(node, []):
                edge_id = (frozenset((node, neighbor)), pos)
                if edge_id in used_edges:
                    continue
                edge = (node, neighbor, pos)
                if neighbor == start and path:
                    result.append(path + [edge])
                elif neighbor not in visited:
                    dfs(
                        neighbor,
                        visited | {neighbor},
                        used_edges | {edge_id},
                        path + [edge],
                    )

        dfs(start, {start}, set(), [])
        return result

    def find_loops(
        self, graph: defaultdict[Any, list]
    ) -> list[list[tuple[str, str, int]]]:
        """Return one representative per distinct closure in the menu, each a
        list of positioned edges. char_loops yields a cycle once per direction
        and once per starting node, so dedup on the canonical edge set."""
        seen = set()
        result = []
        for char in list(graph.keys()):
            for loop in self.char_loops(graph, char):
                key = frozenset((frozenset((frm, to)), pos) for frm, to, pos in loop)
                if key not in seen:
                    seen.add(key)
                    result.append(loop)
        return result

    def get_wire(
        self,
        loop: list[tuple[str, str, int]],
        scramblers: dict[int, dict[str, str]],
    ) -> tuple[str, str] | None:
        """Recover the single plugboard wire for this loop's anchor letter under
        a confirmed rotor state (given its scramblers). Returns (anchor, partner),
        or None if zero or many partners survive (wrong state -> no clean wire)."""
        anchor = loop[0][0]
        survivors = [
            partner
            for partner in self.starter.alphabet
            if self.propagate_is_consistent(loop, scramblers, partner)
        ]
        if len(survivors) == 1:
            return (anchor, survivors[0])
        return None

    def get_plugboard(
        self, loops: list[list[tuple[str, str, int]]], rotor_state
    ) -> list[tuple[str, str]]:
        """Assemble plugboard wires across all loops under a confirmed state.
        The plugboard-free scramblers are built once for every offset used."""
        positions = {pos for loop in loops for _, _, pos in loop}
        scramblers = self.enigma.scramblers_for(rotor_state, positions)

        settings = []
        for loop in loops:
            wire = self.get_wire(loop, scramblers)
            if wire is None:
                continue
            # guard reciprocity
            if wire not in settings and (wire[1], wire[0]) not in settings:
                settings.append(wire)
        return settings

    def propagate_is_consistent(
        self,
        loop: list[tuple[str, str, int]],
        scramblers: dict[int, dict[str, str]],
        assumed_partner: str,
    ) -> bool:
        """Assume the anchor's stecker partner = assumed_partner, propagate it
        around the loop through the precomputed plugboard-free scramblers, and
        report whether it closes back on itself."""
        current = assumed_partner
        for _, _, pos in loop:
            current = scramblers[pos][current]
        return current == assumed_partner

    def has_fixed_point(
        self,
        loop: list[tuple[str, str, int]],
        rotor_state: tuple[tuple[int, int, int], tuple[str, str, str]],
    ) -> bool:
        """Return whether every edge of <loop> holds under <rotor_state>: at
        each hop's offset the machine must map `from` -> `to`. Edges are tested
        in position order so the rotors only ever step forward across the loop.
        (Reciprocity means the directed edge holds whichever way it is stored.)"""
        self.enigma.set_rotor_state(rotor_state)
        done = 0
        for frm, to, pos in loop:
            while done < pos:
                self.enigma.press("A")
                done += 1
            if self.enigma.press(frm) != to:
                return False
            done += 1
        return True

    def decrypt_with(
        self,
        clean_text: str,
        candidate: tuple[tuple[int, int, int], tuple[str, str, str]],
    ) -> str:
        """Instantiate the machine with absolute settings <candidate>
        and type in clean_text to decrypt it."""
        self.enigma.set_rotor_state(candidate)
        return "".join(self.enigma.press(ch) for ch in clean_text)

    def best_target(self, plaintexts: list[str], ioc_threshold=GERMAN_IOC * 0.8) -> str:
        """Return the text in <plaintexts> with lowest chi-squared
        out of those that pass ioc_threshold."""

        def ioc(plaintext: str) -> float:
            counter = Counter(plaintext)
            N = len(plaintext)
            return sum(c * (c - 1) for c in counter.values()) / (N * (N - 1))

        def chi_squared(plaintext: str) -> float:
            counter = Counter(plaintext)
            freq = self.starter.get_german_letter_frequencies()
            n = len(plaintext)
            return sum(
                (counter.get(letter, 0) - p * n) ** 2 / (p * n)
                for letter, p in freq.items()
            )

        above_threshold = []
        for plain in plaintexts:
            if ioc(plain) > ioc_threshold:
                above_threshold.append(plain)

        if not above_threshold:
            return ""

        chi2 = []
        for plain in above_threshold:
            chi2.append(chi_squared(plain))
        return above_threshold[np.argmin(chi2)]

    def build_edges(
        self, clean_text: str, cribs: list[str]
    ) -> dict[tuple[str, int], list[tuple[str, str, int]]]:
        """Return (plain, cipher, rotor_step) edges for every valid
        crib alignment (no letter mapping to itself)."""

        def no_self_map(crib, slice_) -> bool:
            """Return whether any letter in slice_ aligns in crib."""
            return all(c != s for c, s in zip(crib, slice_))

        edges_dct = {}
        for crib in cribs:
            n = len(crib)
            for offset in range(len(clean_text) - n + 1):
                slice_ = clean_text[offset : offset + n]
                if no_self_map(crib, slice_):
                    edges_dct[(crib, offset)] = [
                        (crib[i], slice_[i], offset + i) for i in range(n)
                    ]
        return edges_dct

    def get_graph(
        self, edges: list[tuple[str, str, int]]
    ) -> defaultdict[Any, list[tuple[str, int]]]:
        """Return a graph of each letter and their mapping letters."""
        menu = defaultdict(list)
        for plain, cipher, pos in edges:
            menu[plain].append((cipher, pos))
            menu[cipher].append((plain, pos))
        return menu

    def rotor_states(self) -> list[tuple[tuple[int, int, int], tuple[str, str, str]]]:
        """Return every (rotary_order, rotary_start) the machine could be in:
        each of the 6 rotor orderings paired with each absolute start triple
        (26^3 of them), as ((int, int, int), (str, str, str)) matching
        EnigmaMachine.set_rotor_state."""
        alphabet = self.starter.alphabet

        result = []
        for order in permutations((0, 1, 2)):
            for start in product(alphabet, repeat=3):
                result.append((order, start))
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
    print(f"\n SANITY CHECK \n")
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
    print(f"\n CRACKING \n")
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
    cracker = EnigmaCracker(starter, CRIBS, enigma)
    t0 = time.perf_counter()
    back = cracker.crack(ct)
    elapsed = time.perf_counter() - t0
    print(f"\ncracking-time: {elapsed}s")
    print(f"cracked-text:  {back}")
    print(f"  matches cleaned plaintext? {back == msg}")


if __name__ == "__main__":
    rotary_alphabetic_round_trip_test()
    print()
    rotary_alphabetic_cracking_test()
    print()
