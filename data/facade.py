import json
import random
import string
from math import log10

import numpy as np

from CipherCracking.data.letter_frequencies import LETTER_FREQ
from CipherCracking.data.sample_texts import TEXTS_BY_LENGTH

QUADGRAMS_PATH = "data/quadgrams.json"


class CipherStarter:
    letter_freq: dict[str, float]
    quadgrams: dict[str, float]
    sample_texts_dict: dict[int, str]
    alphabet: str
    log_prob_dict: dict[str, float]
    floor: float

    def __init__(self) -> None:
        self.letter_freq = LETTER_FREQ
        self.quadgrams = self.load_quadgrams(QUADGRAMS_PATH)
        self.sample_texts = TEXTS_BY_LENGTH
        self.alphabet = string.ascii_uppercase
        self.log_prob_dict, self.floor = self.quad_logp_floor(self.quadgrams)

    def random_key(self, seed=None):
        """A random substitution key: a shuffled permutation of A-Z.
        Returned as a 26-char string where key[i] is what letter i maps TO.
        e.g. key[0] is what 'A' becomes."""
        rng = random.Random(seed)
        letters = list(self.alphabet)
        rng.shuffle(letters)
        return "".join(letters)

    def clean_text(self, text: str):
        """Strip to uppercase A-Z only (drop spaces, punctuation, digits).
        Classic substitution works on the bare letter stream."""
        return "".join(ch for ch in text.upper() if ch in self.alphabet)

    def load_quadgrams(self, path: str) -> dict[str, float]:
        """Return a dictionary mapping a representative set of quadgrams
        to their frequency among words in the english language."""
        with open(path, "r") as file:
            data = json.load(file)
        return data

    def quad_logp_floor(self, quadgrams: dict[str, float]):
        """Return (log_prob_dict, floor_log_prob).
        else falls back to the bundled 5,000-quadgrams
        table so the pipeline runs."""
        total = sum(quadgrams.values())
        logp = {g: log10(n / total) for g, n in quadgrams.items()}
        floor = log10(0.01 / total)  # penalty for unseen quadgrams
        return logp, floor

    def fitness(self, text: str):
        """Higher = more English-like. Slide a 4-char window across text; for each
        quadgram add its log-prob (log_prob_dict), or floor if unseen. Return the
        sum."""
        text = self.clean_text(text)
        quadgrams = [text[i : i + 4] for i in range(len(text) - 3)]
        score = 0
        for quad in quadgrams:
            if quad in list(self.log_prob_dict.keys()):
                score += self.log_prob_dict[quad]
            else:
                score += self.floor
        return score

    def vector_to_key(self, vec):
        """vec: array of 26 floats.

        Return a 26-char key string that is a valid permutation of A-Z."""
        order = np.argsort(vec)
        return "".join(self.alphabet[i] for i in order)
