import random

import numpy as np
from numpy import argmax

from cipher import clean_text


def xorText(text: str):
    char_as_bits = [format(ord(char), "08b") for char in clean_text(text)]


def xorTexts(texts: list[str]):
    pass


def sBox() -> tuple[int]:
    """Return a fixed shuffled box of 0, ... ,15"""
    box = list(range(16))
    random.shuffle(box)
    return tuple(box)


def parity(mask: int, value: int) -> int:
    """XOR of the bits of `value` selected by `mask`: AND to select, then parity."""
    return bin(mask & value).count("1") % 2


def bias(a: int, b: int, box: tuple[int]) -> float:
    """Bias of the linear approximation (input mask a, output mask b) over all inputs."""
    matches = sum(1 for x in range(len(box)) if parity(a, x) == parity(b, box[x]))
    return matches / len(box) - 0.5


def lat(box: tuple[int]) -> list[list[float]]:
    return [[bias(a, b, box) for a in range(16)] for b in range(16)]


def bestTail(lat: list[list[float]]) -> list[float]:
    largest, index = sum([np.abs(b) for b in lat[0]]), 0
    for i in range(1, 15, 1):
        magnitude = sum([np.abs(b) for b in lat[i]])
        if magnitude > largest:
            largest, index = magnitude, i
    return lat[index]


def dataAmount(bestTail: list[float]) -> float:
    magnitude = sum([np.abs(b) for b in bestTail])
    return 1 / (magnitude**2)


if __name__ == "__main__":
    lat = lat(sBox())
    print(dataAmount(bestTail(lat)))
