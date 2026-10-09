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
# Same with A=1 (hard totals)
HARD_VALUE = np.array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10], dtype=np.int8)
# Most cards a dealer can draw after the first two (A,A,A,A,A,A,A,5,A,A,A,A + bust card under H17)
DEALER_MAX_HITS = 11


@dataclass
class Hands:
    """Rank/suit arrays for player card 1, player card 2, dealer up, dealer hole.

    draws: (m, DEALER_MAX_HITS) ranks of the cards the dealer would hit with, in order.
    """

    r1: np.ndarray
    s1: np.ndarray
    r2: np.ndarray
    s2: np.ndarray
    ru: np.ndarray
    su: np.ndarray
    rh: np.ndarray
    sh: np.ndarray
    draws: np.ndarray

    @classmethod
    def from_cards(cls, cards):
        """cards: (m,) int8 arrays of card ids in deal order: p1, dealer up, p2, hole, then dealer draws."""
        c1, cu, c2, ch, *draws = cards
        draws = np.stack(draws, axis=1) >> 2 if draws else np.empty((len(c1), 0), dtype=np.int8)
        return cls(c1 >> 2, c1 & 3, c2 >> 2, c2 & 3, cu >> 2, cu & 3, ch >> 2, ch & 3, draws)

    def dealer_hand(self, hits_soft17=False):
        """Play out the dealer's hand -> (best total, number of cards)."""
        hard = HARD_VALUE[self.ru].astype(np.int16) + HARD_VALUE[self.rh]
        has_ace = (self.ru == ACE) | (self.rh == ACE)
        ncards = np.full(hard.shape, 2, dtype=np.int8)
        for k in range(self.draws.shape[1] + 1):
            soft = has_ace & (hard <= 11)
            best = np.where(soft, hard + 10, hard)
            hit = (best < 17) | (hits_soft17 & soft & (best == 17))
            if k == self.draws.shape[1] or not hit.any():
                break
            card = self.draws[:, k]
            hard = hard + np.where(hit, HARD_VALUE[card], 0)
            has_ace |= hit & (card == ACE)
            ncards += hit
        return best, ncards
