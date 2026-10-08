import numpy as np

from .cards import ACE, HEARTS, KING, QUEEN, VALUE, Hands


class SideBet:
    name = ""

    def __init__(self, paytable):
        self.pt = paytable

    def evaluate(self, h: Hands):
        raise NotImplementedError


class PerfectPairs(SideBet):
    name = "perfect_pairs"

    def evaluate(self, h):
        pt = self.pt
        pair = h.r1 == h.r2
        same_suit = h.s1 == h.s2
        same_color = (h.s1 < 2) == (h.s2 < 2)
        res = np.full(h.r1.shape, -1.0)
        res[pair] = pt["mixed"]
        res[pair & same_color] = pt["colored"]
        res[pair & same_suit] = pt["perfect"]
        return res, None


class TwentyOnePlusThree(SideBet):
    name = "21+3"

    def evaluate(self, h):
        pt = self.pt
        flush = (h.s1 == h.s2) & (h.s2 == h.su)
        trips = (h.r1 == h.r2) & (h.r2 == h.ru)
        srt = np.sort(np.stack([h.r1, h.r2, h.ru], axis=1), axis=1).astype(np.int16) + 1  # ace = 1
        a, b, c = srt[:, 0], srt[:, 1], srt[:, 2]
        consecutive = (b == a + 1) & (c == b + 1)
        q_k_a = (a == 1) & (b == 12) & (c == 13)  # ace high; K-A-2 does not wrap
        straight = consecutive | q_k_a

        res = np.full(h.r1.shape, -1.0)
        res[flush] = pt["flush"]
        res[straight] = pt["straight"]
        res[trips] = pt["three_of_a_kind"]
        res[straight & flush] = pt["straight_flush"]
        res[trips & flush] = pt["suited_trips"]
        return res, None


class LuckyLadies(SideBet):
    name = "lucky_ladies"

    def evaluate(self, h):
        pt = self.pt
        total20 = (VALUE[h.r1] + VALUE[h.r2]) == 20
        suited = h.s1 == h.s2
        matched = suited & (h.r1 == h.r2)
        queen_hearts = matched & (h.r1 == QUEEN) & (h.s1 == HEARTS)
        vu, vh = VALUE[h.ru], VALUE[h.rh]
        dealer_bj = ((vu == 10) & (vh == 11)) | ((vu == 11) & (vh == 10))

        res = np.full(h.r1.shape, -1.0)
        res[total20] = pt["total_20"]
        res[total20 & suited] = pt["suited_20"]
        res[total20 & matched] = pt["matched_20"]
        res[total20 & queen_hearts] = pt["queen_hearts_pair"]
        res[total20 & queen_hearts & dealer_bj] = pt["queen_hearts_pair_dealer_bj"]
        return res, None


class RoyalMatch(SideBet):
    name = "royal_match"

    def evaluate(self, h):
        pt = self.pt
        suited = h.s1 == h.s2
        royal = suited & (np.minimum(h.r1, h.r2) == QUEEN) & (np.maximum(h.r1, h.r2) == KING)
        res = np.full(h.r1.shape, -1.0)
        res[suited] = pt["suited"]
        res[royal] = pt["royal"]
        return res, None


class Insurance(SideBet):
    name = "insurance"

    def evaluate(self, h):
        valid = h.ru == ACE  # only offered when the dealer shows an Ace
        res = np.where(VALUE[h.rh] == 10, float(self.pt["win"]), -1.0)
        return res, valid


ALL_BETS = [PerfectPairs, TwentyOnePlusThree, LuckyLadies, RoyalMatch, Insurance]


def build_bets(paytables):
    return [cls(paytables[cls.name]) for cls in ALL_BETS]
