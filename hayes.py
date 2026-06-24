import random
from typing import Any

import random
import numpy as np

STANDARD_SBOX = [
    0xE,
    0x4,
    0xD,
    0x1,
    0x2,
    0xF,
    0xB,
    0x8,
    0x3,
    0xA,
    0x6,
    0xC,
    0x5,
    0x9,
    0x0,
    0x7,
]

STANDARD_PERM = [0, 4, 8, 12, 1, 5, 9, 13, 2, 6, 10, 14, 3, 7, 11, 15]


class HayesCipher:
    sbox: list[int | Any]
    inverse_sbox: list[int | Any]
    perm: list[int]

    def __init__(self, sbox, perm) -> None:
        self.sbox = sbox
        self.perm = perm

        inverse_sbox = [0] * 16
        for i, v in enumerate(self.sbox):
            inverse_sbox[v] = i
        self.inverse_sbox = inverse_sbox

    def generate_keys(self) -> list[list[int]]:
        """Generate 5 random keys of 16 bits."""
        return [[random.randint(0, 1) for _ in range(16)] for _ in range(5)]

    def get_nibbles(self, bit_block: list[int]) -> list[list[int]]:
        """Split the block into 4 groups of 4 bits and return them as lists."""
        return [
            bit_block[i : i + len(bit_block) // 4]
            for i in range(0, len(bit_block), len(bit_block) // 4)
        ]

    def permute(self, bit_block: list[int], inverse: bool = False) -> list[int]:
        """Reorder the 16 bits per the permutation table."""
        result = [0] * 16
        if not inverse:
            for i in range(16):
                result[self.perm[i]] = bit_block[i]
        else:
            for i in range(16):
                result[i] = bit_block[self.perm[i]]
        return result

    def xor_key(self, bit_block, key) -> None:
        """XOR bits in bit_block with those of key."""
        for i in range(16):
            bit_block[i] ^= key[i]

    def int_to_bits(self, val: int, width=4) -> list[int]:
        """Return val as integer in decimal base 2"""
        return [(val >> (width - 1 - i)) & 1 for i in range(width)]

    def bits_to_int(self, bits: list[int]) -> int:
        """Return bits into their integer representation."""
        val = 0
        for b in bits:
            val = (val << 1) | b
        return val

    def encrypt(self, bit_block: list[int], keys: list[list[int]]) -> list[int]:
        """Return a bew copy of input bits encrypted with the given keys."""
        bit_block = bit_block.copy()
        for round_i in range(4):
            self.xor_key(bit_block, keys[round_i])
            if round_i != 3:
                bit_block = self.pass_through_sbox(bit_block)
                bit_block = self.permute(bit_block)
        self.xor_key(bit_block, keys[4])
        return bit_block

    def pass_through_sbox(
        self, bit_block: list[int], inverse: bool = False
    ) -> list[int]:
        """Pass the bits in the block through the sbox once as nibbles."""
        nibbles = self.get_nibbles(bit_block)
        result = []
        for nib in nibbles:
            if not inverse:
                val = self.sbox[self.bits_to_int(nib)]
            else:
                val = self.inverse_sbox[self.bits_to_int(nib)]
            result.extend([b for b in self.int_to_bits(val)])
        return result

    def decrypt(self, bit_block: list[int], keys: list[list[int]]) -> list[int]:
        """Return a bew copy of input bits decrypted with the given keys."""
        bit_block = bit_block.copy()
        self.xor_key(bit_block, keys[4])
        for round_i in range(3, -1, -1):
            if round_i != 3:
                bit_block = self.permute(bit_block, inverse=True)
                bit_block = self.pass_through_sbox(bit_block, inverse=True)
            self.xor_key(bit_block, keys[round_i])
        return bit_block


class HayesCracker:

    def parity(self, mask: int, value: int) -> int:
        """XOR of the bits of `value` selected by `mask`:
        AND to select, then parity."""
        return bin(mask & value).count("1") % 2

    def bias(self, a: int, b: int, sbox: tuple[int, ...]) -> float:
        """Bias of the linear approximation over all inputs."""
        matches = sum(
            1 for x in range(len(sbox)) if self.parity(a, x) == self.parity(b, sbox[x])
        )
        return matches / len(sbox) - 0.5

    def round(self, mask: str | None):
        if not mask:
            mask = [random.randint(0, 1) for _ in range(4)]
        active_boxes = self.get_active_boxes()
        outputs = [box[mask] for box in active_boxes]
        output_choice = random.choice(outputs)


def test_hayes_full_round() -> None:
    """Test that HayesCipher decrypts its own ciphertext
    back to the plaintext."""
    cipher = HayesCipher(STANDARD_SBOX, STANDARD_PERM)
    keys: list[list[int]] = cipher.generate_keys()
    pt = [random.randint(0, 1) for _ in range(16)]

    # CHECK 1: Basic Encryption / Decryption
    ciphertext: list[int] = cipher.encrypt(pt, keys)
    recovered: list[int] = cipher.decrypt(ciphertext, keys)

    print(f"plaintext : {pt}")
    print(f"ciphertext: {ciphertext}")
    print(f"decrypted : {recovered}")
    print(f"round-trip matches? {recovered == pt}")

    # CHECK 2: Hail Mary / Truth Grounds
    for _ in range(100):
        keys = [[random.randint(0, 1) for _ in range(16)] for _ in range(5)]
        pt = [random.randint(0, 1) for _ in range(16)]
        assert cipher.decrypt(cipher.encrypt(pt, keys), keys) == pt


if __name__ == "__main__":
    test_hayes_full_round()
