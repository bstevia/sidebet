class Reporter:
    def __init__(self, config, accs):
        self.cfg = config
        self.accs = accs

    def print(self, elapsed):
        self._summary(elapsed)
        if not self.cfg.shuffle_every_round:
            self._true_count_table()

    def _summary(self, elapsed):
        cfg = self.cfg
        pen = "n/a (fresh shuffle)" if cfg.shuffle_every_round else f"{cfg.penetration:.0%}"
        print(
            f"\nRounds: {cfg.rounds:,} | Decks: {cfg.decks} | Penetration: {pen} | "
            f"Seed: {cfg.seed} | {elapsed:.1f}s ({cfg.rounds / elapsed:,.0f} rounds/s)\n"
        )
        print(f"{'Bet':<15}{'Offered':>13}{'Hit %':>9}{'House edge':>13}{'95% CI (+/-)':>15}{'Std dev':>10}")
        print("-" * 75)
        for name, a in self.accs.items():
            st = a.summary()
            if st is None:
                print(f"{name:<15}{'0':>13}")
                continue
            n, hit, mean, sd, ci = st
            print(f"{name:<15}{int(n):>13,}{hit * 100:>8.2f}%{-mean * 100:>12.2f}%{ci * 100:>14.2f}%{sd:>10.2f}")

    def _true_count_table(self):
        cfg, accs = self.cfg, self.accs
        cap = cfg.tc_cap
        names = list(accs)
        print(f"\nEV - Hi-Lo true count (buckets with >= {cfg.min_bucket:,} samples")
        print(f"{'TC':>5}" + "".join(f"{n:>15}" for n in names))
        print("-" * (5 + 15 * len(names)))
        for b in range(2 * cap + 1):
            row = f"{b - cap:>+5}"
            for n in names:
                a = accs[n]
                if a.n[b] >= cfg.min_bucket:
                    row += f"{a.s[b] / a.n[b] * 100:>14.2f}%"
                else:
                    row += f"{'--':>15}"
            if any(accs[n].n[b] > 0 for n in names):
                print(row)
