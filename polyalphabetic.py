import random

from Cipher_Cracking.data.facade import CipherStarter


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


def polyalphabetic_full_round_test() -> None:
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


if __name__ == "__main__":
    polyalphabetic_full_round_test()
