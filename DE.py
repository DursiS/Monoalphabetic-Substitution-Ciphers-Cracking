"""Crack a monoalphabetic substitution cipher with differential evolution.

Pipeline you're implementing:
    candidate (26 floats in [0,1])  --argsort-->  key permutation
        --decrypt ciphertext-->  text  --quadgram score-->  fitness
    DE searches the 26 floats to MAXIMISE fitness (minimise its negative).

Fill in the three TODOs. Self-checks included; run this file to test as you go.
"""

import numpy as np
import string
from math import log10
from scipy.optimize import differential_evolution

from substitution import ALPHABET, encrypt, decrypt, clean_text, random_key

from quadgrams import QUADGRAMS


def load_quadgrams(path=None):
    """Return (log_prob_dict, floor_logprob).
    else falls back to the bundled 5,000-quadgram table so the pipeline runs."""
    counts = {}
    if path:
        with open(path) as f:
            for line in f:
                gram, n = line.split()
                counts[gram.upper()] = int(n)
    else:
        counts = dict(QUADGRAMS)
    total = sum(counts.values())
    logp = {g: log10(n / total) for g, n in counts.items()}
    floor = log10(0.01 / total)  # penalty for unseen quadgrams
    return logp, floor


QUAD_LOGP, QUAD_FLOOR = load_quadgrams()


def fitness(text: str):
    """Higher = more English-like. Slide a 4-char window across text; for each
    quadgram add its log-prob (QUAD_LOGP), or QUAD_FLOOR if unseen. Return the
    sum."""
    text = clean_text(text)
    quadgrams = [text[i : i + 4] for i in range(len(text) - 3)]
    score = 0
    for quadgram in quadgrams:
        if quadgram in QUAD_LOGP:
            score += QUAD_LOGP[quadgram]
        else:
            score += QUAD_FLOOR
    return score


def vector_to_key(vec):
    """vec: array of 26 floats.

    Return a 26-char key string that is a valid permutation of A-Z."""
    order = np.argsort(vec)
    return "".join(ALPHABET[i] for i in order)


def crack(ciphertext, maxiter=500, popsize=20, seed=0, diff_weight=0.65):
    """Search 26 floats so the decrypted text scores highest."""
    rng = np.random.default_rng(seed)
    population = [rng.random(26) for _ in range(popsize)]  # FLOAT vectors
    scores = [fitness(decrypt(ciphertext, vector_to_key(ind))) for ind in population]

    for _ in range(maxiter):
        for i in range(popsize):
            idxs = rng.choice([j for j in range(popsize) if j != i], 3, replace=False)
            A, B, C = (population[k] for k in idxs)
            trial = np.clip(A + diff_weight * (B - C), 0.0, 1.0)
            trial_score = fitness(decrypt(ciphertext, vector_to_key(trial)))
            if trial_score > scores[i]:
                population[i] = trial
                scores[i] = trial_score

    best = int(np.argmax(scores))
    best_key = vector_to_key(population[best])
    return best_key, decrypt(ciphertext, best_key)


def _climb(ciphertext, key):
    """One hill-climb: repeatedly try swapping every pair of letters in the key,
    keep any swap that raises fitness, stop at a local optimum (no swap helps).
    Returns (key, score)."""
    k = list(key)
    best = fitness(decrypt(ciphertext, "".join(k)))
    improved = True
    while improved:
        improved = False
        for a in range(26):
            for b in range(a + 1, 26):
                k[a], k[b] = k[b], k[a]  # try the swap
                sc = fitness(decrypt(ciphertext, "".join(k)))
                if sc > best:  # uphill -> keep it
                    best = sc
                    improved = True
                else:
                    k[a], k[b] = k[b], k[a]  # downhill -> undo it
    return "".join(k), best


def crack_hillclimb(ciphertext, restarts=20, seed=0):
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
        start = "".join(ALPHABET[i] for i in rng.permutation(26))
        key, score = _climb(ciphertext, start)
        if score > best_score:
            best_score, best_key = score, key
    return best_key, decrypt(ciphertext, best_key)


# --------------------------------------------------------------------------
# Self-checks
# --------------------------------------------------------------------------
if __name__ == "__main__":
    import numpy as np, string

    vec = np.random.default_rng(0).random(26)
    print("".join(string.ascii_uppercase[i] for i in np.argsort(vec)))

    # plain = clean_text("The cat ran bat over the moon to the lawn")
    plain = clean_text("the quick brown fox jumps over the lazy dog these motions")
    key = random_key(seed=42)
    ct = encrypt(plain, key)

    print("=== vector_to_key test ===")
    try:
        k = vector_to_key(np.random.default_rng(0).random(26))
        ok = len(k) == 26 and sorted(k) == list(ALPHABET)
        print(f"  valid permutation? {ok}  ({k})")
    except NotImplementedError:
        print("  not implemented yet")

    print("\n=== fitness should rank English above gibberish ===")
    try:
        good = fitness(plain)
        bad = fitness("XQZJ" * (len(plain) // 4 + 1))
        print(f"  fitness(plaintext)={good:.2f}  fitness(gibberish)={bad:.2f}")
        print(f"  plaintext scores higher? {good > bad}  <-- must be True")
    except NotImplementedError:
        print("  not implemented yet")

    print("\n=== DE Crack ===")
    try:
        best_key, recovered = crack(ct, maxiter=100, popsize=15)
        n_right = sum(a == b for a, b in zip(recovered, plain))
        print(f"  recovered: {recovered}")
        print(f"  exact match? {recovered == plain}")
        print(f"  chars correct: {n_right}/{len(plain)}")
        print(
            "  (Any residual chars are rare letters the top-5k quadgram table"
            " can't disambiguate — a DATA limit; load the full ~390k table"
            " for the last few.)"
        )
    except NotImplementedError:
        print("  not implemented yet")

    print("\n=== Alternative crack: random-restart hill-climbing ===")
    hc_key, hc_recovered = crack_hillclimb(ct, restarts=20)
    hc_right = sum(a == b for a, b in zip(hc_recovered, plain))
    print(f"  recovered: {hc_recovered}")
    print(f"  exact match? {hc_recovered == plain}")
    print(f"  chars correct: {hc_right}/{len(plain)}")
