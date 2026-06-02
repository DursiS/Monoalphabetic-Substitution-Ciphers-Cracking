"""Monoalphabetic substitution cipher — encoder + helpers.
Practice target for cracking with differential evolution later.
"""

import random
import string

ALPHABET = string.ascii_uppercase  # 'ABC...Z'


def random_key(seed=None):
    """A random substitution key: a shuffled permutation of A-Z.
    Returned as a 26-char string where key[i] is what letter i maps TO.
    e.g. key[0] is what 'A' becomes."""
    rng = random.Random(seed)
    letters = list(ALPHABET)
    rng.shuffle(letters)
    return "".join(letters)


def clean_text(text):
    """Strip to uppercase A-Z only (drop spaces, punctuation, digits).
    Classic substitution works on the bare letter stream."""
    return "".join(ch for ch in text.upper() if ch in ALPHABET)


def encrypt(plaintext: str, key: int) -> str:
    """Encrypt by mapping each plaintext letter through the key.
    'A'->key[0], 'B'->key[1], ... built as a lookup table."""
    table = {ALPHABET[i]: key[i] for i in range(26)}
    cleaned = clean_text(plaintext)
    return "".join(table[ch] for ch in cleaned)


def decrypt(ciphertext, key):
    """Decrypt by reversing the key's mapping.
    If 'A'->key[0] on the way in, then key[0]->'A' on the way out."""
    inverse = {key[i]: ALPHABET[i] for i in range(26)}
    return "".join(inverse[ch] for ch in ciphertext if ch in ALPHABET)


if __name__ == "__main__":
    # demo + self-checks
    key = random_key(seed=42)
    print(f"key:        {key}")
    print(f"            {ALPHABET}  (plain, for reference)")

    msg = "The quick brown fox jumps over the lazy dog. Attack at dawn!"
    ct = encrypt(msg, key)
    print(f"\nplaintext:  {clean_text(msg)}")
    print(f"ciphertext: {ct}")

    # CHECK 1: decrypt(encrypt(x)) == x  (round trip with the true key)
    back = decrypt(ct, key)
    print(f"\nround-trip: {back}")
    print(f"  matches cleaned plaintext? {back == clean_text(msg)}")

    # CHECK 2: a WRONG key should NOT recover the message
    wrong = random_key(seed=99)
    print(f"\nwrong-key decrypt: {decrypt(ct, wrong)}")
    print(
        f"  (should be gibberish, != plaintext: {decrypt(ct, wrong) != clean_text(msg)})"
    )
