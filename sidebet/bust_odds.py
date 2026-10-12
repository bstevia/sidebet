"""Exact dealer-bust odds by number of cards, compared with the dealer_bust paytable.

Run: python -m sidebet.bust_odds [--decks 6] [--h17]
"""

import argparse
from functools import lru_cache

from .cards import DEALER_MAX_HITS
from .config import SimConfig
from .paytables import PAYTABLES

MAX_CARDS = 2 + DEALER_MAX_HITS


def bust_probabilities(decks=6, hits_soft17=False):
    """-> tuple p where p[n] = probability the dealer busts with exactly n cards, off the top of a full shoe.

    The player's cards are unseen, so leaving them in the shoe gives the same odds.
    """

    @lru_cache(maxsize=None)
    def play(counts, hard, has_ace, n):
        # counts[v - 1] = cards of value v left in the shoe (1 = ace, 10 = all ten-values)
        out = [0.0] * (MAX_CARDS + 1)
        if hard > 21:
            out[n] = 1.0
            return tuple(out)
        if n >= 2:
            soft = has_ace and hard <= 11
            best = hard + 10 if soft else hard
            if best > 17 or (best == 17 and not (hits_soft17 and soft)):
                return tuple(out)
        left = sum(counts)
        for v, c in enumerate(counts, 1):
            if c:
                rest = counts[: v - 1] + (c - 1,) + counts[v:]
                for k, p in enumerate(play(rest, hard + v, has_ace or v == 1, n + 1)):
                    out[k] += c / left * p
        return tuple(out)

    return play(tuple([4 * decks] * 9 + [16 * decks]), 0, False, 0)


def odds_rows(probs, paytable):
    """-> [(label, probability, payout or None)], one row per card count up to the paytable's largest."""
    top = max(paytable)
    rows = []
    for c in range(3, top + 1):  # a dealer can't bust with fewer than 3 cards
        p = sum(probs[c:]) if c == top else probs[c]
        rows.append((f"{c}+" if c == top and c < MAX_CARDS else str(c), p, paytable.get(c)))
    return rows


def print_report(decks, hits_soft17, paytable):
    probs = bust_probabilities(decks, hits_soft17)
    rows = odds_rows(probs, paytable)
    bust = sum(probs)
    rule = "H17" if hits_soft17 else "S17"
    print(f"\nDealer bust odds | Decks: {decks} | {rule} | Dealer busts {bust:.4%} of hands\n")
    print(f"{'Cards':<8}{'Probability':>13}{'1 in':>13}{'Theo. Prob.':>15}{'Pays':>9}{'Return':>10}")
    print("-" * 68)
    total_return = 0.0
    for label, p, pay in rows:
        ret = p * (pay + 1) if pay is not None else 0.0
        total_return += ret
        pays = f"{pay:g}" if pay is not None else "lose"
        print(f"{label:<8}{p:>12.4%}{1 / p:>13,.1f}{(1 - p) / p:>13,.2f}:1{pays:>9}{ret:>9.4%}")
    print(f"{'No bust':<8}{1 - bust:>12.4%}{1 / (1 - bust):>13,.1f}{'':>15}{'lose':>9}{0:>9.4%}")
    print("-" * 68)
    print(f"{'Total':<8}{1:>12.4%}{'':>37}{total_return:>9.4%}")
    print(f"\nHouse edge: {1 - total_return:.4%}")


def main(argv=None):
    d = SimConfig()
    ap = argparse.ArgumentParser(description="Exact dealer-bust odds by card count vs. the dealer_bust paytable")
    ap.add_argument("--decks", type=int, default=d.decks)
    ap.add_argument("--h17", dest="hits_soft17", action="store_true", help="dealer hits soft 17 (default: stands)")
    args = ap.parse_args(argv)
    print_report(args.decks, args.hits_soft17, PAYTABLES["dealer_bust"])


if __name__ == "__main__":
    main()
