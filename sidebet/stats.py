import math

import numpy as np


class Accumulator:
    def __init__(self, nbuckets):
        self.nb = nbuckets
        self.n = np.zeros(nbuckets)
        self.s = np.zeros(nbuckets)
        self.s2 = np.zeros(nbuckets)
        self.hits = np.zeros(nbuckets)

    def add(self, idx, res, valid):
        if valid is not None:
            idx, res = idx[valid], res[valid]
        nb = self.nb
        self.n += np.bincount(idx, minlength=nb)
        self.s += np.bincount(idx, weights=res, minlength=nb)
        self.s2 += np.bincount(idx, weights=res * res, minlength=nb)
        self.hits += np.bincount(idx[res > 0], minlength=nb)

    def summary(self):
        return summarize(self.n.sum(), self.s.sum(), self.s2.sum(), self.hits.sum())


def summarize(n, s, s2, hits):
    """-> (n, hit_rate, mean, sd, ci95) or None if no samples."""
    if n < 1:
        return None
    mean = s / n
    if n > 1:
        sd = math.sqrt(max((s2 - s * s / n) / (n - 1), 0.0))
        ci = 1.96 * sd / math.sqrt(n)
    else:
        sd = ci = float("nan")
    return n, hits / n, mean, sd, ci
