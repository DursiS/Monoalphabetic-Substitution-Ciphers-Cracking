import numpy as np

from Cipher_Cracking.preprocessing.facade import CipherStarter


class MonoalphabeticCipher:
    starter: CipherStarter

    def __init__(self, starter: CipherStarter) -> None:
        self.starter = starter

    def encrypt(self, plaintext: str, key: int) -> str:
        """Encrypt by mapping each plaintext letter through the key.
        'A'->key[0], 'B'->key[1], ... built as a lookup table."""
        table = {self.starter.alphabet[i]: key[i] for i in range(26)}
        cleaned = self.starter.clean_text(plaintext)
        return "".join(table[ch] for ch in cleaned)

    def decrypt(self, ciphertext, key):
        """Decrypt by reversing the key's mapping.
        If 'A'->key[0] on the way in, then key[0]->'A' on the way out."""
        inverse = {key[i]: self.starter.alphabet[i] for i in range(26)}
        return "".join(inverse[ch] for ch in ciphertext if ch in self.starter.alphabet)

    def crack(self, ciphertext: str, maxiter=500, popsize=20, seed=0, diff_weight=0.65):
        """Search 26 floats so the decrypted text scores highest."""
        rng = np.random.default_rng(seed)
        population = [rng.random(26) for _ in range(popsize)]  # FLOAT vectors
        scores = [
            self.starter.fitness(
                self.decrypt(ciphertext, self.starter.vector_to_key(ind))
            )
            for ind in population
        ]

        for _ in range(maxiter):
            for i in range(popsize):
                idxs = rng.choice(
                    [j for j in range(popsize) if j != i], 3, replace=False
                )
                A, B, C = (population[k] for k in idxs)
                trial = np.clip(A + diff_weight * (B - C), 0.0, 1.0)
                trial_score = self.starter.fitness(
                    self.decrypt(ciphertext, self.starter.vector_to_key(trial))
                )
                if trial_score > scores[i]:
                    population[i] = trial
                    scores[i] = trial_score

        best = int(np.argmax(scores))
        best_key = self.starter.vector_to_key(population[best])
        return best_key, self.decrypt(ciphertext, best_key)

    def _climb(self, ciphertext: str, key: str):
        """One hill-climb: repeatedly try swapping every pair of letters in the key,
        keep any swap that raises fitness, stop at a local optimum (no swap helps).
        Returns (key, score)."""
        k = list(key)
        best = self.starter.fitness(self.decrypt(ciphertext, "".join(k)))
        improved = True
        while improved:
            improved = False
            for a in range(26):
                for b in range(a + 1, 26):
                    k[a], k[b] = k[b], k[a]  # try the swap
                    sc = self.starter.fitness(self.decrypt(ciphertext, "".join(k)))
                    if sc > best:  # uphill -> keep it
                        best = sc
                        improved = True
                    else:
                        k[a], k[b] = k[b], k[a]  # downhill -> undo it
        return "".join(k), best

    def crack_hillclimb(self, ciphertext: str, restarts=20, seed=0):
        """Alternative cracker: random-restart hill-climbing.

        Each restart starts from a random key and climbs (swap two letters, keep the
        swap if the decryption scores higher) until it reaches a local optimum.
        Restarting many times escapes 'good but wrong' local optima; the best climb
        across all restarts wins. On real text (150+ chars) this reliably recovers
        the key, where plain DE stalls.

        Returns (best_key, recovered_plaintext).
        """
        rng = np.random.default_rng(seed)
        best_key, best_score = None, -np.inf
        for _ in range(restarts):
            start = "".join(self.starter.alphabet[i] for i in rng.permutation(26))
            key, score = self._climb(ciphertext, start)
            if score > best_score:
                best_score, best_key = score, key
        return best_key, self.decrypt(ciphertext, best_key)


def monoalphabetic_round_trip_test() -> None:
    """Test that MonoalphabeticCipher encrypts and decrypts properly."""
    # demo + self-checks
    starter = CipherStarter()
    key = starter.random_key(seed=42)
    monoalphabetic = MonoalphabeticCipher(starter)
    print(f"key:        {key}")
    print(f"            {starter.alphabet}  (plain, for reference)")

    msg = "The quick brown fox jumps over the lazy dog. Attack at dawn!"
    ct = monoalphabetic.encrypt(msg, key)
    print(f"\nplaintext:  {starter.clean_text(msg)}")
    print(f"ciphertext: {ct}")

    # CHECK 1: decrypt(encrypt(x)) == x  (round trip with the true key)
    back = monoalphabetic.decrypt(ct, key)
    print(f"\nround-trip: {back}")
    print(f"  matches cleaned plaintext? {back == starter.clean_text(msg)}")

    # CHECK 2: a WRONG key should NOT recover the message
    wrong = starter.random_key(seed=99)
    print(f"\nwrong-key decrypt: {monoalphabetic.decrypt(ct, wrong)}")
    print(
        f"  (should be gibberish, != plaintext: {monoalphabetic.decrypt(ct, wrong) != starter.clean_text(msg)})"
    )


def monoalphabetic_cracking_test() -> None:
    """Test how well MonoalphabeticCipher cracks a representative cipher
    through differential evolution and uphill climb."""
    starter = CipherStarter()
    monoalphabetic = MonoalphabeticCipher(starter)
    vec = np.random.default_rng(0).random(26)
    print("".join(starter.alphabet[i] for i in np.argsort(vec)))

    plain = starter.clean_text(
        "It is a truth universally acknowledged that a single man in "
        "possession of a good fortune must be in want of a wife. However "
        "little known the feelings or views of such a man may be on his first "
        "entering a neighbourhood, this truth is so well fixed in the minds of "
        "the surrounding families that he is considered the rightful property "
        "of some one or other of their daughters."
    )

    # plain = clean_text("the storm passed and a calm morning followed")

    key = starter.random_key(seed=42)
    ct = monoalphabetic.encrypt(plain, key)

    print("\n=== fitness should rank English above gibberish ===")
    try:
        good = starter.fitness(plain)
        bad = starter.fitness("XQZJ" * (len(plain) // 4 + 1))
        print(f"  fitness(plaintext)={good:.2f}  fitness(gibberish)={bad:.2f}")
        print(f"  plaintext scores higher? {good > bad}  <-- must be True")
    except NotImplementedError:
        print("  not implemented yet")

    print("\n=== DE Crack ===")
    try:
        best_key, recovered = monoalphabetic.crack(ct, maxiter=100, popsize=15)
        n_right = sum(a == b for a, b in zip(recovered, plain))
        print(f"  recovered: {recovered}")
        print(f"  exact match? {recovered == plain}")
        print(f"  chars correct: {n_right}/{len(plain)}")

    except NotImplementedError:
        print("  not implemented yet")

    print("\n=== Alternative crack: random-restart hill-climbing ===")
    hc_key, hc_recovered = monoalphabetic.crack_hillclimb(ct, restarts=20)
    hc_right = sum(a == b for a, b in zip(hc_recovered, plain))
    print(f"  recovered: {hc_recovered}")
    print(f"  exact match? {hc_recovered == plain}")
    print(f"  chars correct: {hc_right}/{len(plain)}")


if __name__ == "__main__":
    monoalphabetic_round_trip_test()
    monoalphabetic_cracking_test()
