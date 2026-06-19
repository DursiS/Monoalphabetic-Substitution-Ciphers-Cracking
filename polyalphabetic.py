import random
import time
from collections import Counter

import numpy as np

from Cipher_Cracking.preprocessing.facade import CipherStarter

COLLISION_THRESHOLD = 0.06
ENGLISH_COLLISION = 0.067


class PolyalphabeticCipher:
    starter: CipherStarter
    encryption_table: list[list[int]]
    decryption_table: list[list[int]]

    def __init__(self, starter: CipherStarter) -> None:
        self.starter = starter
        self.encryption_table = self.load_table(True)
        self.decryption_table = self.load_table(False)

    def load_table(self, encrypt: bool) -> list[list[int]]:
        """Return polyalphabetic cipher table using ascii letter indices."""
        row_0 = [i for i in range(26)]
        result = [row_0]
        for j in range(1, 26):
            row_j = row_0[:][j:] + row_0[:][:j]
            result.append(row_j)
        if not encrypt:
            result = [result[0]] + result[::-1][:-1]
        return result

    def fit_key(self, clean_text: str, clean_key: str) -> str:
        """Return key repeated pasted to fit the length of <text>."""
        if not clean_key:
            raise ValueError("key is empty after cleaning")

        fitted_key = clean_key
        while len(fitted_key) < len(clean_text):
            fitted_key += clean_key
        leftover_gap = len(fitted_key) - len(clean_text)
        fitted_key += clean_key[:leftover_gap]
        return fitted_key[: len(clean_text)]

    def encrypt(self, text: str, key: str) -> str:
        """Return an encryption for <text> where each ciphertext letter is the
        ascii index corresponding to intersection between the column of the
        ciphertext and row of the key."""
        clean_text = self.starter.clean_text(text)
        clean_key = self.starter.clean_text(key)
        clean_fit_key = self.fit_key(text, clean_key)
        text_indices = self.starter.text_to_indices(clean_text)
        key_indices = self.starter.text_to_indices(clean_fit_key)

        result = []
        for i, j in zip(key_indices, text_indices):
            result.append(self.encryption_table[i][j])
        return self.starter.indices_to_text(result)

    def decrypt(self, text: str, key: str) -> str:
        """Return the decrypted text given we have a key."""
        clean_text = self.starter.clean_text(text)
        clean_key = self.starter.clean_text(key)
        clean_fit_key = self.fit_key(text, clean_key)
        text_indices = self.starter.text_to_indices(clean_text)
        key_indices = self.starter.text_to_indices(clean_fit_key)

        result = []
        for i, j in zip(key_indices, text_indices):
            result.append(self.decryption_table[i][j])
        return self.starter.indices_to_text(result)

    def counts(self, col: list[str]) -> dict[str, int]:
        """Return a dictionary mapping letters to their count."""
        result = {}
        for ch in set(col):
            result[ch] = col.count(ch)
        return result

    def ioc(self, col: str) -> float:
        """Return the index of coincidence of 2 randomly chosen letters."""
        counts = self.counts(list(col))
        N = len(col)

        result = 0
        for ch in list(counts.keys()):
            result += (counts[ch] * (counts[ch] - 1)) / (N * (N - 1))

        if result < 0 or result > 1:
            raise ValueError
        return result

    def get_columns(self, clean_text: str, key_len: int) -> list[str]:
        """Return a list of columns of text by splitting the text
        by key length."""
        return [clean_text[i::key_len] for i in range(key_len)]

    def get_key_length(
        self, clean_text: str, col_threshold: float, min_len=2, max_len=20
    ) -> int:
        """Return the length of the key"""

        above_threshold = []
        averages, sizes = [], []
        for i in range(min_len, max_len):
            cols = self.get_columns(clean_text, i)
            collisions = np.array([self.ioc(col) for col in cols])
            avg = collisions.mean()
            if avg > col_threshold:
                above_threshold.append(i)
            averages.append(avg)
            sizes.append(i)

        if len(above_threshold) == 0:
            return sizes[np.argmax(averages)]
        return min(above_threshold)

    def chi_squared(self, column: list[str]) -> float:
        """Return chi-squared for letter frequency in column."""
        N = len(column)
        freq = self.starter.get_english_letter_frequencies()
        counts = Counter(column)
        chi2 = 0.0
        for letter, p in freq.items():
            observed = counts.get(letter, 0)
            expected = p * N
            chi2 += (expected - observed) ** 2 / expected
        return chi2

    def crack_key(
        self, clean_text: str, col_threshold: float, min_len=2, max_len=20
    ) -> str:
        """Return the key that makes the most english-like text
        when decrypted."""
        key_len = self.get_key_length(clean_text, col_threshold, min_len, max_len)
        print(f"Recovered key length: {key_len}")
        cols = self.get_columns(clean_text, int(key_len))

        def shift_by_i(ch: str, i: int) -> str:
            """Shift by"""
            idx = (self.starter.alphabet.index(ch) - i) % 26
            return self.starter.alphabet[idx]

        key = ""
        for col in cols:
            chi2 = []
            for shift_i in range(26):
                shifted_col = [shift_by_i(ch, shift_i) for ch in col]
                chi2.append(self.chi_squared(shifted_col))
            key += self.starter.alphabet[int(np.argmin(chi2))]
        return key

    def crack(self, text: str, col_threshold: float, min_len=2, max_len=20) -> str:
        """Return decrypted text."""
        clean_text = self.starter.clean_text(text)
        key = self.crack_key(clean_text, col_threshold, min_len, max_len)
        return self.decrypt(text, key)


def polyalphabetic_round_trip_test() -> None:
    """Test that PolyalphabeticCipher encrypts and can properly
    recover the text by decryption."""
    starter = CipherStarter()
    polyalphabetic = PolyalphabeticCipher(starter)

    length = random.randint(2, 26)
    key = "".join(starter.alphabet[random.randint(0, 25)] for _ in range(length))
    print(f"key:        {key}")
    print(f"            {starter.alphabet}  (plain, for reference)")

    msg = "The quick brown fox jumps over the lazy dog. Attack at dawn!"
    ct = polyalphabetic.encrypt(msg, key)
    print(f"\nplaintext:  {starter.clean_text(msg)}")
    print(f"ciphertext: {ct}")

    # CHECK 1: decrypt(encrypt(x)) == x  (round trip with the true key)
    back = polyalphabetic.decrypt(ct, key)

    print(f"\nround-trip: {back}")
    print(f"  matches cleaned plaintext? {back == starter.clean_text(msg)}")

    # CHECK 2: a WRONG key should NOT recover the message
    wrong = starter.random_key(seed=99)
    print(f"\nwrong-key decrypt: {polyalphabetic.decrypt(ct, wrong)}")
    print(
        f"  (should be gibberish, != plaintext: {polyalphabetic.decrypt(ct, wrong) != starter.clean_text(msg)})"
    )


def polyalphabetic_cracking_test() -> None:
    """Test that PolyalphabeticCipher can crack representative texts,
    and compare the results to that of smaller text sizes."""
    starter = CipherStarter()
    polyalphabetic = PolyalphabeticCipher(starter)

    length = random.randint(2, 20)
    key = "".join(starter.alphabet[random.randint(0, 25)] for _ in range(length))
    print(f"key:        {key}")
    print(f"key length:        {len(key)}")

    # msg = "The quick brown fox jumps over the lazy dog. Attack at dawn!"
    msg = starter.clean_text(
        "It is a truth universally acknowledged that a single man in "
        "possession of a good fortune must be in want of a wife. However "
        "little known the feelings or views of such a man may be on his first "
        "entering a neighbourhood, this truth is so well fixed in the minds of "
        "the surrounding families that he is considered the rightful property "
        "of some one or other of their daughters."
    )
    ct = polyalphabetic.encrypt(msg, key)
    print(f"\nplaintext:  {starter.clean_text(msg)}")
    print(f"ciphertext: {ct}")

    # CHECK 1: crack(encrypt(x)) == msg
    t0 = time.perf_counter()
    back = polyalphabetic.crack(ct, COLLISION_THRESHOLD)
    elapsed = time.perf_counter() - t0
    print(f"\ncracking-time: {elapsed}s")
    print(f"\ncracked-text: {back}")
    print(f"  matches cleaned plaintext? {back == starter.clean_text(msg)}")


if __name__ == "__main__":
    # polyalphabetic_round_trip_test()
    polyalphabetic_cracking_test()
