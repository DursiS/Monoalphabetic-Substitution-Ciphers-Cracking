import random
import string
from collections import Counter

import numpy as np

from CipherCracking.data.sample_texts import SAMPLE_TEXTS
from CipherCracking.DE import fitness
from CipherCracking.modernCiphers import ModernTextCipher
from CipherCracking.substitution import clean_text, encrypt

ALPHABET = string.ascii_uppercase


def getEntropy(text: str) -> float:
    """Return the entropy of <text> based on its letter distribution."""
    counts = Counter(text)
    n = len(text)
    bits = sum([(c / n) * np.log(c / n) for c in counts.values()])
    return -bits


def textType(raw_text: str, entropy_means, fitness_means, allowed_error=0.25) -> str:
    """Return the estimated type of text of <text>."""
    entropy_mid = (entropy_means["PLAIN"] + entropy_means["SUBSTITUTION"]) * 0.5

    if np.abs(getEntropy(clean_text(raw_text)) - entropy_mid) < allowed_error:
        if np.abs(fitness(raw_text) - fitness_means["SUBSTITUTION"]) < np.abs(
            fitness(raw_text) - fitness_means["PLAIN"]
        ):
            return "SUBSTITUTION"
        else:
            return "PLAIN"
    else:
        return "MODERN"


def getSubstitutedTexts(plain_texts: list[str]) -> list[str]:
    """Return a list of substituted texts from texts in <plain_texts>."""
    vec: np.ndarray = np.random.default_rng(0).random(26)
    key: str = "".join(string.ascii_uppercase[i] for i in np.argsort(vec))

    return [encrypt(raw_text, key) for raw_text in plain_texts]


def getModernTexts(plain_texts: list[str]) -> list[str]:
    """Return a list of modern encrypted texts from texts in <plain_texts>."""
    modern = ModernTextCipher()
    return [modern.encrypt(raw_text) for raw_text in plain_texts]


SUBSTITUTED = getSubstitutedTexts(SAMPLE_TEXTS)
MODERN = getModernTexts(SAMPLE_TEXTS)


def identificationFrequency(
    plain_texts: list[str], entropy_means, fitness_means
) -> dict[str, float]:
    """Return the frequency of identification of textType of
    texts in <texts>."""
    identifications, n = {}, len(plain_texts)

    # Plain
    for raw_text in plain_texts:
        if "PLAIN" not in identifications:
            identifications["PLAIN"] = 0
        if textType(raw_text, entropy_means, fitness_means) == "PLAIN":
            identifications["PLAIN"] += 1
    identifications["PLAIN"] = identifications["PLAIN"] / n

    # Substitution
    for cipher in SUBSTITUTED:
        if "SUBSTITUTION" not in identifications:
            identifications["SUBSTITUTION"] = 0
        if textType(cipher, entropy_means, fitness_means) == "SUBSTITUTION":
            identifications["SUBSTITUTION"] += 1
    identifications["SUBSTITUTION"] = identifications["SUBSTITUTION"] / n

    # Modern
    for encrypted in MODERN:
        if "MODERN" not in identifications:
            identifications["MODERN"] = 0
        if textType(encrypted, entropy_means, fitness_means) == "MODERN":
            identifications["MODERN"] += 1
    identifications["MODERN"] = round(identifications["MODERN"] / n, 4)

    return identifications


def textTypeEntropies(plain_texts: list[str]) -> dict[str, float]:
    """Return a dictionary of textType to average entropy amount
    sample texts."""

    return {
        "PLAIN": np.array([getEntropy(text) for text in plain_texts]).mean(),
        "SUBSTITUTION": np.array([getEntropy(text) for text in SUBSTITUTED]).mean(),
        "MODERN": np.array([getEntropy(text) for text in MODERN]).mean(),
    }


def textTypeFitness(plain_texts: list[str]) -> dict[str, float]:
    """Return a dictionary of textType to average fitness of sample texts."""
    return {
        "PLAIN": np.array([fitness(text) for text in plain_texts]).mean(),
        "SUBSTITUTION": np.array([fitness(text) for text in SUBSTITUTED]).mean(),
        "MODERN": np.array([fitness(text) for text in MODERN]).mean(),
    }


if __name__ == "__main__":

    entropy_means = textTypeEntropies(SAMPLE_TEXTS)
    print(
        f"== Average Entropies ==\n"
        f"Plain: {entropy_means["PLAIN"]}\n"
        f"Substitution: {entropy_means["SUBSTITUTION"]}\n"
        f"Modern: {entropy_means["MODERN"]}\n"
    )

    fitness_means = textTypeFitness(SAMPLE_TEXTS)
    print(
        f"== Average Fitness ==\n"
        f"Plain: {fitness_means["PLAIN"]}\n"
        f"Substitution: {fitness_means["SUBSTITUTION"]}\n"
        f"Modern: {fitness_means["MODERN"]}\n"
    )

    freq = identificationFrequency(SAMPLE_TEXTS, entropy_means, fitness_means)
    print(
        f"== TextType Identification Frequency ==\n"
        f"Plain: {freq["PLAIN"]}\n"
        f"Substitution: {freq["SUBSTITUTION"]}\n"
        f"Modern: {freq["MODERN"]}\n"
    )
