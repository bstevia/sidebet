from dataclasses import dataclass


@dataclass
class SimConfig:
    rounds: int = 10_000_000
    decks: int = 6
    penetration: float = 0.75  # fraction of shoe dealt before reshuffle
    extra_cards: int = 6  # cards consumed per round beyond the first 4
    shuffle_every_round: bool = False  # fresh shoe each round (no count effects)
    seed: int = 12345
    tc_cap: int = 6  # clamp true-count buckets to +/- this value
    min_bucket: int = 2000  # min samples to show a true-count bucket
    batch_cards: int = 8_000_000  # approx. cards per batch (memory knob)

    def validate(self):
        if not 0.1 <= self.penetration <= 0.95:
            raise SystemExit("--penetration must be between 0.1 and 0.95")
        if self.decks * 52 < 4 + self.extra_cards:
            raise SystemExit("Shoe too small for one round.")
