"""
Card id = rank * 4 + suit, so rank = id >> 2, suit = id & 3.
rank 0=A, 1=2 ... 8=9, 9=10, 10=J, 11=Q, 12=K; suit 0=hearts, 1=diamonds, 2=clubs, 3=spades
"""

from dataclasses import dataclass

import numpy as np

QUEEN, KING, ACE = 11, 12, 0
HEARTS = 0

# Hi-Lo: 2-6 => +1, 7-9 => 0, 10/J/Q/K/A => -1
HILO = np.array([-1, 1, 1, 1, 1, 1, 0, 0, 0, -1, -1, -1, -1], dtype=np.int16)
# Blackjack values: A=11, 2-9 face value, 10/J/Q/K=10
VALUE = np.array([11, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10], dtype=np.int8)


@dataclass
class Hands:
    """Rank/suit arrays for player card 1, player card 2, dealer up, dealer hole."""

    r1: np.ndarray
    s1: np.ndarray
    r2: np.ndarray
    s2: np.ndarray
    ru: np.ndarray
    su: np.ndarray
    rh: np.ndarray
    sh: np.ndarray

    @classmethod
    def from_cards(cls, cards):
        """cards: four (m,) int8 arrays of card ids in deal order: p1, dealer up, p2, hole."""
        c1, cu, c2, ch = cards
        return cls(c1 >> 2, c1 & 3, c2 >> 2, c2 & 3, cu >> 2, cu & 3, ch >> 2, ch & 3)
