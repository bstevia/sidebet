import argparse
import time

from .config import SimConfig
from .report import Reporter
from .simulator import Simulator


def parse_args(argv=None):
    d = SimConfig()
    ap = argparse.ArgumentParser(description="Blackjack side-bet Monte Carlo simulator (NumPy)")
    ap.add_argument("--rounds", type=int, default=d.rounds)
    ap.add_argument("--decks", type=int, default=d.decks)
    ap.add_argument("--penetration", type=float, default=d.penetration, help="fraction of shoe dealt before reshuffle")
    ap.add_argument("--extra-cards", type=int, default=d.extra_cards, help="cards consumed per round beyond the first 4")
    ap.add_argument("--shuffle-every-round", action="store_true", help="fresh shoe each round (no count effects)")
    ap.add_argument("--h17", dest="hits_soft17", action="store_true", help="dealer hits soft 17 (default: stands)")
    ap.add_argument("--seed", type=int, default=d.seed)
    ap.add_argument("--tc-cap", type=int, default=d.tc_cap, help="clamp true-count buckets to +/- this value")
    ap.add_argument("--min-bucket", type=int, default=d.min_bucket, help="min samples to show a true-count bucket")
    ap.add_argument("--batch-cards", type=int, default=d.batch_cards, help="approx. cards per batch (memory knob)")
    return SimConfig(**vars(ap.parse_args(argv)))


def main(argv=None):
    config = parse_args(argv)
    config.validate()
    t0 = time.perf_counter()
    accs = Simulator(config).run()
    Reporter(config, accs).print(time.perf_counter() - t0)
