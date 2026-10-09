import numpy as np

from .bets import build_bets
from .cards import DEALER_MAX_HITS, HILO, Hands
from .paytables import PAYTABLES
from .stats import Accumulator

CARDS_DEALT = 4 + DEALER_MAX_HITS


class Simulator:
    def __init__(self, config):
        self.cfg = config
        self.rng = np.random.default_rng(config.seed)
        self.bets = build_bets(PAYTABLES, config)
        self.accs = {b.name: Accumulator(2 * config.tc_cap + 1) for b in self.bets}

    def run(self):
        if self.cfg.shuffle_every_round:
            self._run_fresh_shuffle()
        else:
            self._run_shoes()
        return self.accs

    def _tally(self, idx, cards):
        hands = Hands.from_cards(cards)
        for bet in self.bets:
            res, valid = bet.evaluate(hands)
            self.accs[bet.name].add(idx, res, valid)

    @staticmethod
    def rounds_per_shoe(n_cards, cut, cards_per_round, cards_needed):
        """Rounds dealt per shoe: a round starts only if pos < cut and cards_needed cards remain."""
        pos = np.arange(0, n_cards // cards_per_round + 1) * cards_per_round
        return int(np.sum((pos < cut) & (n_cards - pos >= max(cards_per_round, cards_needed))))

    def _sample_fresh_hands(self, m):
        """First CARDS_DEALT cards of m freshly shuffled shoes, drawn without replacement."""
        n = self.cfg.decks * 52
        chosen = np.empty((m, CARDS_DEALT), dtype=np.int64)
        for j in range(CARDS_DEALT):
            x = self.rng.integers(0, n - j, size=m)
            prev = np.sort(chosen[:, :j], axis=1)
            for col in range(j):  # skip already-taken positions, ascending
                x = x + (x >= prev[:, col])
            chosen[:, j] = x
        ids = (chosen % 52).astype(np.int8)
        return [ids[:, j] for j in range(CARDS_DEALT)]

    def _run_fresh_shuffle(self):
        cfg = self.cfg
        remaining = cfg.rounds
        chunk = max(1, cfg.batch_cards // 8)
        while remaining > 0:
            m = min(chunk, remaining)
            cards = self._sample_fresh_hands(m)
            idx = np.full(m, cfg.tc_cap, dtype=np.int64)  # true count is 0 for a fresh shoe
            self._tally(idx, cards)
            remaining -= m

    def _run_shoes(self):
        cfg = self.cfg
        n_cards = cfg.decks * 52
        cpr = 4 + cfg.extra_cards
        cap = cfg.tc_cap
        cut = int(n_cards * cfg.penetration)
        rps = self.rounds_per_shoe(n_cards, cut, cpr, CARDS_DEALT)
        if rps < 1:
            raise SystemExit("No rounds fit in a shoe with these settings.")
        base = np.arange(52, dtype=np.int8)
        starts = np.arange(rps) * cpr
        rem_decks = (n_cards - starts) / 52.0
        shoes_per_batch = max(1, cfg.batch_cards // n_cards)
        remaining = cfg.rounds

        while remaining > 0:
            s = min(shoes_per_batch, -(-remaining // rps))
            shoes = self.rng.permuted(np.tile(np.tile(base, cfg.decks), (s, 1)), axis=1)

            # Running Hi-Lo count before each round = prefix sum at the round's start.
            run = np.zeros((s, n_cards + 1), dtype=np.int16)
            np.cumsum(HILO[shoes >> 2], axis=1, dtype=np.int16, out=run[:, 1:])
            true_count = run[:, starts] / rem_decks
            bucket = np.clip(np.rint(true_count), -cap, cap).astype(np.int64) + cap

            take = min(s * rps, remaining)
            cards = [shoes[:, starts + j].reshape(-1)[:take] for j in range(CARDS_DEALT)]
            self._tally(bucket.reshape(-1)[:take], cards)
            remaining -= take
