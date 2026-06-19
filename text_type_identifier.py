from collections import Counter
from typing import Any

import numpy as np
from numpy import floating

from Cipher_Cracking.data.facade import CipherStarter
from Cipher_Cracking.data.sample_texts import SAMPLE_TEXTS
from Cipher_Cracking.fernet_modern import ModernTextCipher
from Cipher_Cracking.monoalphabetic import MonoalphabeticCipher


class TextTypeIdentifier:
    """Classify a text as PLAIN, SUBSTITUTION, or MODERN.

    Two signals, calibrated on a sample corpus at construction:
      - letter-distribution entropy: MODERN ciphertext is near-uniform (high
        entropy), classical text is not -- this peels MODERN off first.
      - English quadgram fitness: separates PLAIN from SUBSTITUTION (a
        substitution preserves letter frequencies, so entropy alone can't).
    """

    starter: CipherStarter

    def __init__(self, starter: CipherStarter, plain_texts: list[str]) -> None:
        self.starter = starter
        self.substitution = MonoalphabeticCipher(starter)
        self.modern = ModernTextCipher()

        self.plain_texts = plain_texts
        self.substituted = self.substitute_texts(plain_texts)
        self.modern_texts = self.modernize_texts(plain_texts)

        self.entropy_means = self.text_type_entropies()
        self.fitness_means = self.text_type_fitness()

    def get_entropy(self, text: str) -> float:
        """Return the entropy of <text> based on its letter distribution."""
        counts = Counter(text)
        n = len(text)
        bits = sum((c / n) * np.log(c / n) for c in counts.values())
        return -bits

    def substitute_texts(self, plain_texts: list[str]) -> list[str]:
        """Substitution-encrypt every text with one fixed random key."""
        key = self.starter.vector_to_key(np.random.default_rng(0).random(26))
        return [self.substitution.encrypt(text, key) for text in plain_texts]

    def modernize_texts(self, plain_texts: list[str]) -> list[str]:
        """Modern (Fernet) encrypt every text."""
        return [self.modern.encrypt(text) for text in plain_texts]

    def text_type_entropies(self) -> dict[str, floating[Any]]:
        """Average letter-distribution entropy per text type (cleaned to A-Z)."""
        clean = self.starter.clean_text
        return {
            "PLAIN": np.mean([self.get_entropy(clean(t)) for t in self.plain_texts]),
            "SUBSTITUTION": np.mean(
                [self.get_entropy(clean(t)) for t in self.substituted]
            ),
            "MODERN": np.mean([self.get_entropy(clean(t)) for t in self.modern_texts]),
        }

    def text_type_fitness(self) -> dict[str, floating[Any]]:
        """Average English quadgram fitness per text type."""
        fitness = self.starter.fitness
        return {
            "PLAIN": np.mean([fitness(t) for t in self.plain_texts]),
            "SUBSTITUTION": np.mean([fitness(t) for t in self.substituted]),
            "MODERN": np.mean([fitness(t) for t in self.modern_texts]),
        }

    def text_type(self, raw_text: str, allowed_error: float = 0.25) -> str:
        """Return the estimated type of <raw_text>: PLAIN, SUBSTITUTION, or MODERN."""
        entropy_mid = (
            self.entropy_means["PLAIN"] + self.entropy_means["SUBSTITUTION"]
        ) * 0.5
        cleaned = self.starter.clean_text(raw_text)

        if np.abs(self.get_entropy(cleaned) - entropy_mid) < allowed_error:
            score = self.starter.fitness(raw_text)
            to_sub = np.abs(score - self.fitness_means["SUBSTITUTION"])
            to_plain = np.abs(score - self.fitness_means["PLAIN"])
            return "SUBSTITUTION" if to_sub < to_plain else "PLAIN"
        return "MODERN"

    def identification_frequency(self) -> dict[str, float]:
        """Identify the fraction of each calibrated corpus that text_
        type() labels correctly."""
        n = len(self.plain_texts)
        corpora = {
            "PLAIN": self.plain_texts,
            "SUBSTITUTION": self.substituted,
            "MODERN": self.modern_texts,
        }
        return {
            label: round(sum(self.text_type(t) == label for t in texts) / n, 4)
            for label, texts in corpora.items()
        }


def text_type_identification_test() -> None:
    """Build the identifier on the sample corpus and report how well it
    separates PLAIN / SUBSTITUTION / MODERN text."""
    starter = CipherStarter()
    identifier = TextTypeIdentifier(starter, SAMPLE_TEXTS)

    em = identifier.entropy_means
    print("== Average Entropies ==")
    print(f"  Plain:        {em['PLAIN']:.4f}")
    print(f"  Substitution: {em['SUBSTITUTION']:.4f}")
    print(f"  Modern:       {em['MODERN']:.4f}\n")

    fm = identifier.fitness_means
    print("== Average Fitness ==")
    print(f"  Plain:        {fm['PLAIN']:.2f}")
    print(f"  Substitution: {fm['SUBSTITUTION']:.2f}")
    print(f"  Modern:       {fm['MODERN']:.2f}\n")

    freq = identifier.identification_frequency()
    print("== Identification Accuracy (fraction correct) ==")
    print(f"  Plain:        {freq['PLAIN']}")
    print(f"  Substitution: {freq['SUBSTITUTION']}")
    print(f"  Modern:       {freq['MODERN']}")


if __name__ == "__main__":
    text_type_identification_test()
