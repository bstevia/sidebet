"""
Card-counting systems, selected with --count. Edit or add systems here.

Tags are listed by rank: A, 2, 3, 4, 5, 6, 7, 8, 9, 10, J, Q, K.
Fractional tags (e.g. Wong Halves) are fine; they're scaled to integers internally.
Unbalanced systems (tags don't sum to 0 over a deck) are bucketed by running count
instead of true count, starting from an initial running count that puts the shoe's
final count at one deck's worth of tags (KO: 4 - 4 * decks).
"""

from dataclasses import dataclass
from fractions import Fraction
from math import lcm

import numpy as np


@dataclass(frozen=True)
class CountSystem:
    label: str
    tags: tuple

    @property
    def scale(self):
        """Smallest integer that turns every tag into an integer."""
        return lcm(*(Fraction(t).limit_denominator(100).denominator for t in self.tags))

    @property
    def int_tags(self):
        return np.array([round(t * self.scale) for t in self.tags], dtype=np.int32)

    @property
    def balanced(self):
        return self.int_tags.sum() == 0

    def initial_count(self, decks):
        """Initial running count, in scaled units."""
        return int(self.int_tags.sum()) * 4 * (1 - decks)


T1, T2 = (-1,) * 4, (-2,) * 4  # 10, J, Q, K

COUNT_SYSTEMS = {
    "hilo": CountSystem("Hi-Lo", (-1, 1, 1, 1, 1, 1, 0, 0, 0) + T1),
    "ko": CountSystem("KO", (-1, 1, 1, 1, 1, 1, 1, 0, 0) + T1),
    "hiopt1": CountSystem("Hi-Opt I", (0, 0, 1, 1, 1, 1, 0, 0, 0) + T1),
    "hiopt2": CountSystem("Hi-Opt II", (0, 1, 1, 2, 2, 1, 1, 0, 0) + T2),
    "omega2": CountSystem("Omega II", (0, 1, 1, 2, 2, 2, 1, 0, -1) + T2),
    "zen": CountSystem("Zen", (-1, 1, 1, 2, 2, 2, 1, 0, 0) + T2),
    "halves": CountSystem("Wong Halves", (-1, 0.5, 1, 1, 1.5, 1, 0.5, 0, -0.5) + T1),
}
