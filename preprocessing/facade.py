import json
import random
import string
from math import log10

import numpy as np

from Cipher_Cracking.data.letter_frequencies import LETTER_FREQ
from Cipher_Cracking.data.sample_texts import TEXTS_BY_LENGTH
from Enigma.sample_messages import MESSAGES


QUADGRAMS_PATH = "data/quadgrams.json"


class CipherStarter:
    letter_freq: dict[str, float]
    quadgrams: dict[str, float]
    sample_texts_dict: dict[int, str]
    alphabet: str
    log_prob_dict: dict[str, float]
    floor: float
    sample_german_texts: list[str]

    def __init__(self) -> None:
        self.letter_freq = LETTER_FREQ
        self.quadgrams = self.load_quadgrams(QUADGRAMS_PATH)
        self.sample_texts = TEXTS_BY_LENGTH
        self.alphabet = string.ascii_uppercase
        self.log_prob_dict, self.floor = self.quad_logp_floor(self.quadgrams)
        self.sample_german_texts = self.load_german_messages()

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

    def text_to_indices(self, text: str) -> list[int]:
        """Return a list of integer 0-25 corresponding to each letter's
        order in the alphabet."""
        return [self.alphabet.index(ch) for ch in text]

    def indices_to_text(self, indices: list[int]) -> str:
        """Return the text for which each index in <indices<
        corresponds to its position in the alphabet."""
        return "".join(self.alphabet[idx] for idx in indices)

    def load_german_messages(self) -> list[str]:
        """Return a list of WWII German sample communications."""
        return MESSAGES

    def get_english_letter_frequencies(self) -> dict[str, float]:
        return {
            "A": 0.08167,
            "B": 0.01492,
            "C": 0.02782,
            "D": 0.04253,
            "E": 0.12702,
            "F": 0.02228,
            "G": 0.02015,
            "H": 0.06094,
            "I": 0.06966,
            "J": 0.00153,
            "K": 0.00772,
            "L": 0.04025,
            "M": 0.02406,
            "N": 0.06749,
            "O": 0.07507,
            "P": 0.01929,
            "Q": 0.00095,
            "R": 0.05987,
            "S": 0.06327,
            "T": 0.09056,
            "U": 0.02758,
            "V": 0.00978,
            "W": 0.02360,
            "X": 0.00150,
            "Y": 0.01974,
            "Z": 0.00074,
        }

    def get_german_letter_frequencies(self) -> dict[str, float]:
        return {
            "A": 0.0651,
            "B": 0.0189,
            "C": 0.0306,
            "D": 0.0508,
            "E": 0.1740,
            "F": 0.0166,
            "G": 0.0301,
            "H": 0.0476,
            "I": 0.0755,
            "J": 0.0027,
            "K": 0.0121,
            "L": 0.0344,
            "M": 0.0253,
            "N": 0.0978,
            "O": 0.0251,
            "P": 0.0079,
            "Q": 0.0002,
            "R": 0.0700,
            "S": 0.0727,
            "T": 0.0615,
            "U": 0.0435,
            "V": 0.0067,
            "W": 0.0189,
            "X": 0.0003,
            "Y": 0.0004,
            "Z": 0.0113,
        }
