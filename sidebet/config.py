from dataclasses import dataclass

from .cards import DEALER_MAX_HITS
from .counts import COUNT_SYSTEMS


@dataclass
class SimConfig:
    rounds: int = 10_000_000
    decks: int = 6
    penetration: float = 0.75  # fraction of shoe dealt before reshuffle
    extra_cards: int = 6  # cards consumed per round beyond the first 4
    shuffle_every_round: bool = False  # fresh shoe each round (no count effects)
    hits_soft17: bool = False  # dealer hits soft 17 (H17) instead of standing (S17)
    count_system: str = "hilo"  # key into COUNT_SYSTEMS (sidebet/counts.py)
    seed: int = 12345
    tc_cap: int = 6  # clamp count buckets to +/- this value
    min_bucket: int = 2000  # min samples to show a count bucket
    batch_cards: int = 8_000_000  # approx. cards per batch (memory knob)

    def validate(self):
        if not 0.1 <= self.penetration <= 0.95:
            raise SystemExit("--penetration must be between 0.1 and 0.95")
        if self.decks * 52 < 4 + max(self.extra_cards, DEALER_MAX_HITS):
            raise SystemExit("Shoe too small for one round.")
        if self.count_system not in COUNT_SYSTEMS:
            raise SystemExit(f"Unknown count system {self.count_system!r}; choose from {', '.join(COUNT_SYSTEMS)}")
